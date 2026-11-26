#!/usr/bin/env python3
"""Detect a repository's stack and name the references an audit should read.

The detector looks at file names and dependency manifests. It does not install
packages and it does not execute the target application. The repository is
untrusted input: a manifest that resolves outside it, for example through a
symlink, or that is larger than MAX_MANIFEST_BYTES, is skipped.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from pathlib import Path

SIGNALS = (
    ("nextjs", ("next.config.js", "next.config.mjs", "next.config.ts"), ("next",)),
    ("react", (), ("react",)),
    ("supabase", ("supabase/config.toml",), ("@supabase/supabase-js", "@supabase/ssr")),
    ("firebase", ("firebase.json", "firestore.rules"), ("firebase", "firebase-admin")),
    ("stripe", (), ("stripe",)),
    ("django", ("manage.py",), ("django", "Django")),
    ("fastapi", (), ("fastapi",)),
)

MAX_MANIFEST_BYTES = 2 * 1024 * 1024


def contained_file(root: Path, path: Path) -> bool:
    """True when path is a regular file whose real location is inside root."""
    try:
        real = path.resolve(strict=True)
    except (OSError, RuntimeError):
        return False
    return real.is_relative_to(root.resolve()) and real.is_file() and real.stat().st_size <= MAX_MANIFEST_BYTES


REFERENCES = {
    "nextjs": "references/framework-specific/nextjs.md",
    "react": "references/framework-specific/react.md",
    "supabase": "references/framework-specific/supabase.md",
    "firebase": "references/framework-specific/firebase.md",
    "stripe": "references/framework-specific/stripe.md",
    "django": "references/framework-specific/django.md",
    "fastapi": "references/framework-specific/fastapi.md",
}


def read_manifest_names(root: Path) -> set[str]:
    names: set[str] = set()
    package = root / "package.json"
    if contained_file(root, package):
        try:
            document = json.loads(package.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            document = {}
        for field in ("dependencies", "devDependencies", "peerDependencies"):
            value = document.get(field) or {}
            if isinstance(value, dict):
                names.update(value)
    for filename in ("requirements.txt", "requirements-dev.txt", "Pipfile"):
        path = root / filename
        if not contained_file(root, path):
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            token = line.strip().split("==")[0].split(">=")[0].split("[")[0].strip()
            if token and not token.startswith("#"):
                names.add(token)
    pyproject = root / "pyproject.toml"
    if contained_file(root, pyproject):
        names.update(pyproject_dependencies(pyproject))
    return names


def pyproject_dependencies(path: Path) -> set[str]:
    """Read declared dependencies only, so a comment or description does not count."""
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8", errors="replace"))
    except tomllib.TOMLDecodeError:
        return set()
    specs: list[str] = []
    project = document.get("project") or {}
    specs.extend(project.get("dependencies") or [])
    for group in (project.get("optional-dependencies") or {}).values():
        specs.extend(group or [])
    for group in (document.get("dependency-groups") or {}).values():
        specs.extend(item for item in group or [] if isinstance(item, str))
    poetry = (document.get("tool") or {}).get("poetry") or {}
    specs.extend(poetry.get("dependencies") or {})
    for group in (poetry.get("group") or {}).values():
        specs.extend((group or {}).get("dependencies") or {})
    names: set[str] = set()
    for spec in specs:
        token = re.split(r"[\s\[<>=!~;@(]", str(spec).strip(), maxsplit=1)[0]
        if token:
            names.add(token)
            names.add(token.lower())
    return names


def detect(root: Path) -> list[str]:
    found: list[str] = []
    manifests = read_manifest_names(root)
    for stack, files, packages in SIGNALS:
        if any((root / relative).exists() for relative in files) or any(name in manifests for name in packages):
            found.append(stack)
    if "nextjs" in found and "react" not in found:
        found.append("react")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect which Application Guardian references apply.")
    parser.add_argument("root", nargs="?", type=Path, default=Path("."), help="Application repository to inspect")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"Directory not found: {root}", file=sys.stderr)
        return 2
    stacks = detect(root)
    if not stacks:
        print("No framework-specific reference detected. Use the technology-independent references.")
        return 0
    print("Read these framework references:")
    for stack in stacks:
        print(f"  {REFERENCES[stack]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
