#!/usr/bin/env python3
"""Re-run the commands recorded in an audit, in CI, and write the evidence.

The audit file says which command proved each runtime check. This script runs
those commands itself, on the checked-out commit, and records what happened.
The release gate then compares the audit with this file, so a PASS counts only
if CI saw the command pass.

Usage:
    python scripts/ci_evidence.py docs/audits/audit-result.json --out "$RUNNER_TEMP/guardian"

The output folder must be outside the repository, so the evidence cannot be
committed by mistake and does not count as an uncommitted change.

Commands run without a shell, from the repository root, with a short list of
environment variables and a time limit. The first word must be an allowed
test runner. This is not a sandbox: an allowed runner such as python can run
any code, just as the repository's own tests can. What protects CI is review:
audit-result.json, the tests, and the workflow change only through reviewed
pull requests. See docs/ci.md.

Exit 0 when the evidence file was written, whatever the commands returned.
The gate decides. Exit 2 when the evidence cannot be produced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import queue
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from guardianlib import CI_SCHEMA_VERSION, INLINE_CODE, TEST_RUNNERS, recorded_runs, runner_name

ALLOWED_RUNNERS = TEST_RUNNERS

# Only these variables reach the commands. Tokens and secrets do not.
KEPT_ENVIRONMENT = (
    "PATH",
    "HOME",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "TMPDIR",
    "TEMP",
    "TMP",
    "TERM",
    "CI",
    "SYSTEMROOT",
    "PATHEXT",
    "COMSPEC",
    "USERPROFILE",
    "APPDATA",
    "LOCALAPPDATA",
)

MAX_LOG_BYTES = 5 * 1024 * 1024

# Run metadata the evidence records. Not secret, and kept when the runner
# restarts itself with a clean environment.
RUN_METADATA = ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_REPOSITORY")
CLEAN_MARKER = "GUARDIAN_CLEAN_ENVIRONMENT"


def restart_clean(keep: list[str]) -> None:
    """Re-run this script with only the variables it needs.

    A command can read its parent's environment through /proc, so removing
    secrets from the child alone is not enough. On POSIX the runner replaces
    itself with a copy that never held them. Other platforms keep the parent
    environment; see docs/ci.md.
    """
    if os.name != "posix" or os.environ.get(CLEAN_MARKER) == "1":
        return
    names = (*KEPT_ENVIRONMENT, *RUN_METADATA, *keep)
    environment = {name: os.environ[name] for name in names if name in os.environ}
    environment[CLEAN_MARKER] = "1"
    os.execve(sys.executable, [sys.executable, os.path.abspath(__file__), *sys.argv[1:]], environment)


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *arguments], capture_output=True, text=True, check=False, timeout=30
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def resolve_program(argv: list[str], root: Path, allowed: frozenset[str]) -> str | None:
    """Return why the command may not run, or None when it may."""
    if not argv:
        return "the command is empty"
    program = argv[0]
    name = runner_name(shlex.join(argv))
    if name not in allowed:
        return f"{program} is not an allowed test runner (add it with --allow)"
    if INLINE_CODE.get(name, set()) & set(argv[1:]):
        return f"{program} would run inline code instead of a test file"
    if "/" in program or "\\" in program:
        target = (root / program).resolve()
        if not target.is_relative_to(root):
            return f"{program} is outside the repository"
        if not target.is_file():
            return f"{program} does not exist"
    elif shutil.which(program) is None:
        return f"{program} is not installed"
    return None


def stop_group(process: subprocess.Popen) -> None:
    """Kill the command and anything it started, so nothing keeps running after it."""
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elif process.poll() is None:
        process.kill()


def run(argv: list[str], root: Path, log: Path, timeout: int, environment: dict[str, str]) -> dict:
    """Run one command, keeping at most MAX_LOG_BYTES of its output on disk.

    output_sha256 covers everything read from the command; log_sha256 covers
    the log that is kept. Output past the limit is hashed, then dropped, so a
    noisy command cannot fill the disk. Reading stops at the time limit, or one
    second after the command exits, even if something it started still holds
    the output open.
    """
    started = now()
    total = hashlib.sha256()
    kept = hashlib.sha256()
    size = 0
    process = subprocess.Popen(
        argv,
        cwd=root,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=os.name == "posix",
    )
    chunks: queue.Queue = queue.Queue()

    def pump() -> None:
        for chunk in iter(lambda: process.stdout.read(65536), b""):
            chunks.put(chunk)
        chunks.put(None)

    threading.Thread(target=pump, daemon=True).start()
    deadline = time.monotonic() + timeout
    exited_at = None
    timed_out = False
    with log.open("wb") as handle:
        while True:
            now_ = time.monotonic()
            if now_ >= deadline:
                timed_out = process.poll() is None
                break
            if process.poll() is not None:
                exited_at = exited_at or now_
                if now_ - exited_at > 1:
                    break
            try:
                chunk = chunks.get(timeout=0.1)
            except queue.Empty:
                continue
            if chunk is None:
                break
            total.update(chunk)
            room = MAX_LOG_BYTES - size
            if room > 0:
                handle.write(chunk[:room])
                kept.update(chunk[:room])
            size += len(chunk)
    stop_group(process)
    exit_code = process.wait()
    return {
        "exit_code": None if timed_out else exit_code,
        "timed_out": timed_out,
        "started_at": started,
        "finished_at": now(),
        "output_bytes": size,
        "output_sha256": total.hexdigest(),
        "log_sha256": kept.hexdigest(),
        "log_truncated": size > MAX_LOG_BYTES,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-run an audit's recorded commands and write CI evidence.")
    parser.add_argument("audit_json", type=Path, help="Path to audit-result.json")
    parser.add_argument("--out", type=Path, required=True, help="Folder for the evidence, outside the repository")
    parser.add_argument("--timeout", type=int, default=900, help="Seconds allowed per command (default 900)")
    parser.add_argument("--allow", action="append", default=[], help="Allow another test runner by name")
    parser.add_argument(
        "--keep-env", action="append", default=[], help="Pass another environment variable to the commands"
    )
    args = parser.parse_args()
    restart_clean(args.keep_env)

    audit_path = args.audit_json.resolve()
    if not audit_path.is_file():
        print(f"Audit file not found: {args.audit_json}", file=sys.stderr)
        return 2
    raw = audit_path.read_bytes()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"Audit file is not JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(document, dict):
        print("Audit file must contain a JSON object.", file=sys.stderr)
        return 2

    top = git(audit_path.parent, "rev-parse", "--show-toplevel")
    head = git(audit_path.parent, "rev-parse", "HEAD")
    if not top or not head:
        print("The audit file is not inside a Git repository with a commit.", file=sys.stderr)
        return 2
    root = Path(top).resolve()
    out = args.out.resolve()
    if out.is_relative_to(root):
        print(f"--out must be outside the repository ({root}).", file=sys.stderr)
        return 2
    logs = out / "logs"
    logs.mkdir(parents=True, exist_ok=True)

    allowed = ALLOWED_RUNNERS | frozenset(args.allow)
    environment = {name: os.environ[name] for name in (*KEPT_ENVIRONMENT, *args.keep_env) if name in os.environ}
    environment["CI"] = "true"
    environment.pop(CLEAN_MARKER, None)

    # One run per distinct command. Several checks may share a command.
    by_command: dict[str, list[str]] = {}
    for item_id, command in recorded_runs(document):
        by_command.setdefault(command, []).append(item_id)

    runs = []
    for index, (command, ids) in enumerate(by_command.items(), start=1):
        entry: dict = {"ids": ids, "command": command}
        try:
            argv = shlex.split(command)
        except ValueError as exc:
            argv = []
            entry["rejected"] = f"the command cannot be parsed: {exc}"
        if "rejected" not in entry:
            problem = resolve_program(argv, root, allowed)
            if problem:
                entry["rejected"] = problem
        if "rejected" in entry:
            entry["exit_code"] = None
            print(f"[{', '.join(ids)}] not run: {entry['rejected']}")
        else:
            log = logs / f"run-{index:03d}.log"
            entry["argv"] = argv
            entry["log"] = log.relative_to(out).as_posix()
            entry.update(run(argv, root, log, args.timeout, environment))
            result = "timed out" if entry["timed_out"] else f"exit {entry['exit_code']}"
            print(f"[{', '.join(ids)}] {command}: {result}")
        runs.append(entry)

    evidence = {
        "schema_version": CI_SCHEMA_VERSION,
        "generated_by": "application-guardian ci_evidence.py",
        "commit": head,
        "repository": os.environ.get("GITHUB_REPOSITORY", ""),
        "run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
        "audit_file": audit_path.relative_to(root).as_posix(),
        "audit_sha256": hashlib.sha256(raw).hexdigest(),
        "generated_at": now(),
        "runs": runs,
    }
    target = out / "ci-evidence.json"
    target.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
