#!/usr/bin/env python3
"""Detect a repository's stack and name the references an audit should read.

The detector looks at file names and dependency manifests. It does not install
packages and it does not execute the target application.
"""

from __future__ import annotations

import argparse
import json
import sys
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
    if package.is_file():
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
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            token = line.strip().split("==")[0].split(">=")[0].split("[")[0].strip()
            if token and not token.startswith("#"):
                names.add(token)
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8", errors="replace").lower()
        for candidate in ("django", "fastapi", "stripe"):
            if candidate in text:
                names.add(candidate)
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
