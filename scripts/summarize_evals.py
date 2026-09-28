#!/usr/bin/env python3
"""Summarize manually graded Felicity behavior eval results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, help="one host and timestamp result directory")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    paths = sorted(args.results.glob("*.json"))
    if not paths:
        parser.error("no case result JSON files found")

    passed = 0
    graded = 0
    pending = 0
    for path in paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        criteria = record.get("criteria_to_grade", [])
        grades = record.get("grades", [])
        if len(grades) != len(criteria) or any(value not in (0, 1, None) for value in grades):
            parser.error(f"invalid grades in {path}")
        case_passed = sum(value == 1 for value in grades)
        case_graded = sum(value is not None for value in grades)
        passed += case_passed
        graded += case_graded
        pending += len(grades) - case_graded
        print(
            f"{record.get('id', path.stem)}: {case_passed}/{case_graded} graded; "
            f"{len(grades) - case_graded} pending; status={record.get('status')}"
        )
    print(f"Total: {passed}/{graded} graded criteria passed; {pending} pending")
    return 1 if args.require_complete and pending else 0


if __name__ == "__main__":
    raise SystemExit(main())
