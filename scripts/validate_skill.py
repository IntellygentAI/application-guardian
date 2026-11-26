#!/usr/bin/env python3
"""Validate the Application Guardian skill layout, frontmatter, and links.

Exit 0 when the skill matches the Agent Skills constraints used by this
repository. Exit 1 when a check fails.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "AGENTS.md",
    "references/functional-testing.md",
    "references/security-testing.md",
    "references/data-privacy.md",
    "references/legal-exposure.md",
    "references/database-security.md",
    "references/api-security.md",
    "references/payment-security.md",
    "references/ai-security.md",
    "references/accessibility.md",
    "references/production-readiness.md",
    "references/mobile-security.md",
    "references/agent-mcp-security.md",
    "references/threat-modelling.md",
    "references/supply-chain-security.md",
    "references/verification-protocol.md",
    "references/finding-verification.md",
    "references/framework-specific/nextjs.md",
    "references/framework-specific/react.md",
    "references/framework-specific/supabase.md",
    "references/framework-specific/firebase.md",
    "references/framework-specific/stripe.md",
    "references/framework-specific/django.md",
    "references/framework-specific/fastapi.md",
    "templates/audit-report.md",
    "templates/threat-model.md",
    "templates/test-matrix.md",
    "templates/release-checklist.md",
    "templates/finding.json",
    "schemas/audit.schema.json",
    "schemas/finding.schema.json",
    "scripts/scaffold_audit.py",
    "scripts/validate_skill.py",
    "scripts/detect_stack.py",
    "scripts/validate_report.py",
    "scripts/release_gate.py",
    "scripts/ci_evidence.py",
    "templates/ci/guardian-release.yml",
    "templates/ci/CODEOWNERS",
    "evals/evals.json",
    "docs/installation.md",
    "docs/compatibility.md",
    "docs/architecture.md",
    "docs/ci.md",
    "docs/benchmarks.md",
    "docs/coverage-matrix.md",
    "examples/sample-audit.md",
    "examples/sample-security-findings.md",
    "examples/sample-audit-result.json",
)

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"```.*?```", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("SKILL.md frontmatter is not closed")
    data: dict = {}
    meta: dict[str, str] | None = None
    lines = text[4:end].splitlines()
    index = 0

    while index < len(lines):
        raw = lines[index]
        if not raw.strip():
            index += 1
            continue
        if raw.startswith((" ", "\t")):
            raise ValueError(f"Unexpected indented frontmatter line: {raw}")
        if ":" not in raw:
            raise ValueError(f"Cannot parse frontmatter line: {raw}")
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key == "metadata" and value == "":
            meta = {}
            data["metadata"] = meta
            index += 1
            while index < len(lines) and lines[index].startswith((" ", "\t")):
                nested = lines[index].strip()
                index += 1
                if ":" not in nested:
                    raise ValueError(f"Cannot parse metadata line: {nested}")
                nested_key, nested_value = nested.split(":", 1)
                nested_value = nested_value.strip()
                if nested_value in {">-", ">", "|"}:
                    parts: list[str] = []
                    while index < len(lines) and lines[index].startswith((" ", "\t")):
                        parts.append(lines[index].strip())
                        index += 1
                    meta[nested_key.strip()] = " ".join(part for part in parts if part)
                else:
                    meta[nested_key.strip()] = nested_value.strip('"').strip("'")
            meta = None
            continue
        if value in {">-", ">", "|"}:
            parts = []
            index += 1
            while index < len(lines) and lines[index].startswith((" ", "\t")):
                parts.append(lines[index].strip())
                index += 1
            data[key] = " ".join(part for part in parts if part)
            continue
        data[key] = value.strip('"').strip("'")
        index += 1
    return data


def check_frontmatter(errors: list[str]) -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > 500:
        errors.append(f"SKILL.md is {len(lines)} lines. Keep it under 500.")
    try:
        meta = parse_frontmatter(text)
    except ValueError as exc:
        errors.append(str(exc))
        return
    name = str(meta.get("name") or "")
    if name != ROOT.name:
        errors.append(f"name must match the directory name {ROOT.name!r}, got {name!r}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append("name must be lowercase letters, numbers, and single hyphens")
    description = str(meta.get("description") or "")
    if not description or len(description) > 1024:
        errors.append("description must be 1 to 1024 characters")
    if meta.get("license") != "MIT":
        errors.append("license must be MIT")
    compatibility = str(meta.get("compatibility") or "")
    if compatibility and len(compatibility) > 500:
        errors.append("compatibility must be at most 500 characters")
    metadata = meta.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be a map of strings")
        return
    for key in ("author", "version"):
        value = metadata.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"metadata.{key} must be a non-empty string")
    if metadata.get("author") != "IntellygentAI":
        errors.append("metadata.author must be IntellygentAI")
    if metadata.get("version") != "0.4.0":
        errors.append("metadata.version must be 0.4.0 until measured benchmarks exist")


def check_files(errors: list[str]) -> None:
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"Missing {relative}")


def check_links(errors: list[str]) -> None:
    files = [
        ROOT / "SKILL.md",
        ROOT / "README.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "AGENTS.md",
        ROOT / "CHANGELOG.md",
        ROOT / "SECURITY.md",
    ]
    files.extend(path for path in (ROOT / "references").rglob("*.md"))
    files.extend(path for path in (ROOT / "docs").glob("*.md"))
    files.extend(path for path in (ROOT / "examples").glob("*.md"))
    for path in files:
        text = FENCE.sub("", path.read_text(encoding="utf-8"))
        for match in LINK.finditer(text):
            target = match.group(1)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            relative = target.split("#", 1)[0]
            if not relative:
                continue
            resolved = (path.parent / relative).resolve()
            if not resolved.is_file():
                errors.append(f"{path.relative_to(ROOT)} links to missing {target}")


def validate() -> list[str]:
    errors: list[str] = []
    check_files(errors)
    if (ROOT / "SKILL.md").is_file():
        check_frontmatter(errors)
    check_links(errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Application Guardian skill.")
    parser.parse_args()
    errors = validate()
    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(f"Skill validation OK ({len(REQUIRED)} required files) at {ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
