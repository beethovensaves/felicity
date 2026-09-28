#!/usr/bin/env python3
"""Run Felicity behavior cases in an isolated Codex or Claude Code workspace."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE_FILE = ROOT / "evals/cases.json"
SKILLS = {"felicity-review", "felicity-write"}


def load_cases() -> list[dict]:
    data = json.loads(CASE_FILE.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("cases"), list):
        raise ValueError("evals/cases.json must have version 1 and a cases list")
    cases = data["cases"]
    ids: set[str] = set()
    for case in cases:
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            raise ValueError(f"missing or duplicate case id: {case_id!r}")
        ids.add(case_id)
        if case.get("skill") not in SKILLS:
            raise ValueError(f"{case_id}: unknown skill")
        if case.get("invocation", "explicit") not in {"explicit", "implicit"}:
            raise ValueError(f"{case_id}: invocation must be explicit or implicit")
        if not isinstance(case.get("prompt"), str) or not case["prompt"]:
            raise ValueError(f"{case_id}: missing prompt")
        if not isinstance(case.get("criteria"), list) or not case["criteria"]:
            raise ValueError(f"{case_id}: missing criteria")
        if not all(isinstance(item, str) and item for item in case["criteria"]):
            raise ValueError(f"{case_id}: invalid criterion")
        if not isinstance(case.get("protected_literals"), list):
            raise ValueError(f"{case_id}: protected_literals must be a list")
        if not all(isinstance(item, str) and item for item in case["protected_literals"]):
            raise ValueError(f"{case_id}: invalid protected literal")
    return cases


def stage_skills(host: str, skills_root: Path, workspace: Path) -> None:
    destination = workspace / (".agents/skills" if host == "codex" else ".claude/skills")
    destination.mkdir(parents=True)
    for name in sorted(SKILLS):
        source = skills_root / name
        if not (source / "SKILL.md").is_file():
            raise ValueError(f"missing skill: {source / 'SKILL.md'}")
        shutil.copytree(source, destination / name)


def command_for(host: str, workspace: Path, prompt: str, final_path: Path) -> list[str]:
    if host == "codex":
        return [
            "codex", "exec", "--ephemeral", "--skip-git-repo-check",
            "--ignore-user-config", "--sandbox", "read-only", "--json",
            "-C", str(workspace), "-o", str(final_path), prompt,
        ]
    return [
        "claude", "-p", "--no-session-persistence", "--output-format", "text",
        "--tools", "Read,Skill", "--setting-sources", "project", prompt,
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=("codex", "claude"))
    parser.add_argument("--case", action="append", dest="case_ids")
    parser.add_argument("--skills-root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=ROOT / "evals/results")
    parser.add_argument("--list", action="store_true", help="list cases without a model run")
    parser.add_argument("--run", action="store_true", help="execute selected cases")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    try:
        cases = load_cases()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    if args.list:
        for case in cases:
            print(f"{case['id']}\t{case['skill']}")
        return 0
    if not args.host:
        parser.error("--host is required unless --list is used")
    if args.timeout < 1:
        parser.error("--timeout must be positive")

    selected = [case for case in cases if not args.case_ids or case["id"] in args.case_ids]
    unknown = set(args.case_ids or []) - {case["id"] for case in cases}
    if unknown:
        parser.error(f"unknown case ids: {', '.join(sorted(unknown))}")
    if not args.run:
        print(f"{len(selected)} cases selected for {args.host}. Add --run to execute model calls.")
        return 0

    executable = "codex" if args.host == "codex" else "claude"
    if shutil.which(executable) is None:
        parser.error(f"{executable} is not installed")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    result_dir = args.out.resolve() / args.host / stamp
    result_dir.mkdir(parents=True, exist_ok=True)
    failures = 0
    for case in selected:
        with tempfile.TemporaryDirectory(prefix="felicity-eval-") as temporary:
            workspace = Path(temporary)
            stage_skills(args.host, args.skills_root.resolve(), workspace)
            invoke = "$" if args.host == "codex" else "/"
            prompt = (
                f"Use {invoke}{case['skill']} for this task.\n\n{case['prompt']}"
                if case.get("invocation", "explicit") == "explicit"
                else case["prompt"]
            )
            final_path = workspace / "final.txt"
            command = command_for(args.host, workspace, prompt, final_path)
            try:
                result = subprocess.run(
                    command, cwd=workspace, text=True, capture_output=True,
                    timeout=args.timeout, check=False,
                )
                final = (
                    final_path.read_text(encoding="utf-8")
                    if args.host == "codex" and final_path.is_file()
                    else result.stdout
                )
                status = "captured" if result.returncode == 0 and final.strip() else "run-failed"
                stderr = result.stderr
                trace = result.stdout if args.host == "codex" else ""
            except subprocess.TimeoutExpired as exc:
                final = ""
                stderr = str(exc)
                trace = ""
                status = "timed-out"

        missing_literals = [
            literal for literal in case["protected_literals"]
            if literal.casefold() not in final.casefold()
        ]
        record = {
            "id": case["id"],
            "host": args.host,
            "status": status,
            "skills_root": str(args.skills_root.resolve()),
            "invocation": case.get("invocation", "explicit"),
            "missing_protected_literals": missing_literals,
            "criteria_to_grade": case["criteria"],
            "grades": [None] * len(case["criteria"]),
            "note": "Literal checks are signals, not a semantic grade. Score the criteria against final.txt.",
        }
        prefix = result_dir / case["id"]
        prefix.with_suffix(".json").write_text(json.dumps(record, indent=2) + "\n")
        prefix.with_suffix(".txt").write_text(final, encoding="utf-8")
        prefix.with_suffix(".stderr.txt").write_text(stderr, encoding="utf-8")
        if trace:
            prefix.with_suffix(".trace.jsonl").write_text(trace, encoding="utf-8")
        print(f"{case['id']}: {status}; {len(missing_literals)} missing protected literals")
        if status != "captured":
            failures += 1
    print(f"Results: {result_dir}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
