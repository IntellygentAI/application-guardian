#!/usr/bin/env python3
"""Validate an audit-result.json file against schemas/audit.schema.json.

Uses the Python standard library. Exit 0 when the document matches the schema.
Exit 1 when it does not. Exit 2 when the file cannot be read.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"


def load_schema(name: str) -> dict[str, Any]:
    path = SCHEMAS / Path(name).name
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _type_ok(instance: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "boolean":
        return isinstance(instance, bool)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "null":
        return instance is None
    return False


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    if "$ref" in schema:
        return validate_instance(instance, load_schema(schema["$ref"]), path)

    expected = schema.get("type")
    if isinstance(expected, list):
        if not any(_type_ok(instance, item) for item in expected):
            errors.append(f"{path} must be one of {expected}")
            return errors
    elif isinstance(expected, str) and not _type_ok(instance, expected):
        errors.append(f"{path} must be {expected}")
        return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path} must equal {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path} must be one of {schema['enum']}")
    if isinstance(instance, str) and "minLength" in schema and len(instance) < schema["minLength"]:
        errors.append(f"{path} must not be empty")

    if isinstance(instance, dict):
        required = schema.get("required") or []
        for key in required:
            if key not in instance:
                errors.append(f"{path}.{key} is required")
        properties = schema.get("properties") or {}
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{path}.{key} is not allowed")
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate_instance(value, properties[key], f"{path}.{key}"))

    if isinstance(instance, list) and "items" in schema:
        for index, item in enumerate(instance):
            errors.extend(validate_instance(item, schema["items"], f"{path}[{index}]"))
    return errors


def validate_audit(document: Any) -> list[str]:
    if not isinstance(document, dict):
        return ["$ must be an object"]
    return validate_instance(document, load_schema("audit.schema.json"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Application Guardian audit JSON file.")
    parser.add_argument("audit_json", type=Path)
    args = parser.parse_args()
    if not args.audit_json.is_file():
        print(f"Audit file not found: {args.audit_json}", file=sys.stderr)
        return 2
    try:
        document = json.loads(args.audit_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Audit file is not JSON: {exc}", file=sys.stderr)
        return 2
    errors = validate_audit(document)
    if errors:
        print(f"{args.audit_json} is invalid:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(f"{args.audit_json} matches schemas/audit.schema.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
