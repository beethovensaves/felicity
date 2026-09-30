#!/usr/bin/env python3
"""Sample and run EditEval/IteraTeR and PUB with a matched Codex baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import shutil
import subprocess
import tempfile
import zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = 20260929
MODEL = "gpt-6-astra"
REASONING_EFFORT = "medium"
EDIT_INSTRUCTIONS = {
    "clarity": "Make the text clearer",
    "coherence": "Make the text more cohesive",
    "fluency": "Fix grammar errors",
}


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def prepare(iterater_test: Path, pub_dir: Path, output: Path, count: int) -> None:
    from nltk.tokenize.treebank import TreebankWordDetokenizer

    rng = random.Random(SEED)
    detokenize = TreebankWordDetokenizer().detokenize
    edit_rows = [json.loads(line) for line in iterater_test.read_text(encoding="utf-8").splitlines()]
    edit_sample = {}
    for task in EDIT_INSTRUCTIONS:
        unique = {}
        for index, row in enumerate(edit_rows):
            if row["labels"] != task or len(row["after_sent"]) <= 1:
                continue
            source = detokenize(row["before_sent"].split(" ")).strip()
            unique.setdefault(source, {
                "source_index": index,
                "input": source,
                "reference": detokenize(row["after_sent"].split(" ")).strip(),
            })
        if len(unique) < count:
            raise ValueError(f"{task} has only {len(unique)} unique eligible examples")
        edit_sample[task] = rng.sample(list(unique.values()), count)

    pub_sample = {}
    for task in range(1, 15):
        archive = pub_dir / f"task_{task}.zip"
        with zipfile.ZipFile(archive) as zipped:
            rows = [json.loads(line) for line in zipped.read(f"task_{task}.jsonl").decode().splitlines()]
        valid = [row for row in rows if row["correct answer"] in row["options"]]
        if len(valid) < count:
            raise ValueError(f"PUB task {task} has only {len(valid)} valid examples")
        pub_sample[str(task)] = [
            {
                "source_id": row["id"],
                "pretext": row["pretext"],
                "options": row["options"],
                "answer_index": row["options"].index(row["correct answer"]) + 1,
            }
            for row in rng.sample(valid, count)
        ]

    save_json(output, {
        "version": 1,
        "seed": SEED,
        "count_per_task": count,
        "sources": {
            "editeval": "https://github.com/facebookresearch/EditEval",
            "iterater_test": "https://huggingface.co/datasets/wanyu/IteraTeR_human_sent/resolve/main/test.json",
            "pub": "https://huggingface.co/datasets/cfilt/PUB/tree/main/data",
            "sha256": {
                "iterater_test": sha256(iterater_test),
                "pub_task_archives": {
                    str(task): sha256(pub_dir / f"task_{task}.zip") for task in range(1, 15)
                },
            },
        },
        "editeval": edit_sample,
        "pub": pub_sample,
    })


def make_prompt(benchmark: str, task: str, rows: list[dict], skilled: bool) -> str:
    if benchmark == "editeval":
        prefix = (
            "Use $felicity-write. Read .agents/skills/felicity-write/SKILL.md, "
            ".agents/skills/felicity-write/references/writing-standard.md, and "
            ".agents/skills/felicity-write/references/anti-slop.md before editing.\n\n"
            if skilled else ""
        )
        parts = [
            prefix + "Apply the instruction independently to each numbered text. ",
            "Return one revised sentence per item, in the same order, in the required JSON answers array. ",
            f"Instruction: {EDIT_INSTRUCTIONS[task]}\n",
        ]
        parts.extend(f"\nItem {i}: {row['input']}\n" for i, row in enumerate(rows, 1))
    else:
        prefix = (
            "Use $felicity-review. Read .agents/skills/felicity-review/SKILL.md and "
            ".agents/skills/felicity-review/references/review-standard.md before answering. "
            "Examine what each utterance conveys in context. "
            if skilled else "Examine what each utterance conveys in context. "
        )
        parts = [
            prefix + "For each numbered item, choose the best option. ",
            "Return only the 1-based option number for each item, in order, in the required JSON answers array. ",
            "Answer the questions; do not report review findings.\n",
        ]
        for i, row in enumerate(rows, 1):
            parts.append(f"\nItem {i}:\n{row['pretext'].strip()}\nOptions:\n")
            parts.extend(f"{j}. {option.strip()}\n" for j, option in enumerate(row["options"], 1))
    return "".join(parts)


def schema_for(benchmark: str, count: int) -> dict:
    item = {"type": "string"} if benchmark == "editeval" else {"type": "integer", "minimum": 1}
    return {
        "type": "object",
        "properties": {"answers": {"type": "array", "items": item, "minItems": count, "maxItems": count}},
        "required": ["answers"],
        "additionalProperties": False,
    }


def run_batch(manifest: dict, output: Path, benchmark: str, task: str, skilled: bool, timeout: int) -> dict:
    rows = manifest[benchmark][task]
    mode = "felicity" if skilled else "baseline"
    name = f"{benchmark}-{task}"
    prefix = output / mode / name
    prompt = make_prompt(benchmark, task, rows, skilled)
    schema = schema_for(benchmark, len(rows))
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".prompt.txt").write_text(prompt, encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="felicity-public-bench-") as temporary:
        workspace = Path(temporary)
        if skilled:
            skills_dir = workspace / ".agents/skills"
            skills_dir.mkdir(parents=True)
            skill = "felicity-write" if benchmark == "editeval" else "felicity-review"
            shutil.copytree(ROOT / skill, skills_dir / skill)
        schema_path = workspace / "schema.json"
        final_path = workspace / "final.json"
        save_json(schema_path, schema)
        global_felicity = [
            home / skill / "SKILL.md"
            for home in (Path.home() / ".codex/skills", Path.home() / ".agents/skills")
            for skill in ("felicity-review", "felicity-write")
            if (home / skill / "SKILL.md").is_file()
        ]
        overrides = [{"path": str(path), "enabled": False} for path in global_felicity]
        config_value = "skills.config=[" + ",".join(
            "{path=" + json.dumps(item["path"]) + ",enabled=false}" for item in overrides
        ) + "]"
        command = [
            "codex", "exec", "--ephemeral", "--skip-git-repo-check", "--ignore-user-config",
            "-m", MODEL, "-c", f'model_reasoning_effort="{REASONING_EFFORT}"', "-c", config_value,
            "--sandbox", "read-only", "--json", "--output-schema", str(schema_path),
            "-C", str(workspace), "-o", str(final_path), "-",
        ]
        try:
            result = subprocess.run(command, input=prompt, text=True, capture_output=True, timeout=timeout)
            final = final_path.read_text(encoding="utf-8") if final_path.is_file() else ""
            events = []
            for line in result.stdout.splitlines():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            skill_read_paths = sorted({
                match
                for event in events
                if event.get("item", {}).get("type") == "command_execution"
                for match in re.findall(r"(/[^\s'\"]+/SKILL\.md)", event.get("item", {}).get("command", ""))
            })
            skill_read = bool(skill_read_paths)
            usage = next((event.get("usage") for event in reversed(events) if event.get("type") == "turn.completed"), None)
            error = result.stderr.strip() if result.returncode else ""
            if result.returncode and not error:
                error = next((event.get("message", "") for event in events if event.get("type") == "error"), "")
            status = "captured" if result.returncode == 0 and final else "failed"
            if status == "captured" and skilled and not skill_read:
                status = "skill-not-read"
            if status == "captured" and not skilled and skill_read:
                status = "baseline-contaminated"
        except subprocess.TimeoutExpired as exc:
            final, skill_read, skill_read_paths, usage, error, status = "", False, [], None, str(exc), "timed-out"

    prefix.with_suffix(".final.json").write_text(final, encoding="utf-8")
    record = {
        "benchmark": benchmark, "task": task, "mode": mode, "status": status,
        "model": MODEL, "reasoning_effort": REASONING_EFFORT,
        "skill_read": skill_read, "skill_read_paths": skill_read_paths,
        "disabled_global_felicity": sorted({path.parent.name for path in global_felicity}),
        "usage": usage, "error": error,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    save_json(prefix.with_suffix(".meta.json"), record)
    return record


def run(manifest_path: Path, output: Path, timeout: int, workers: int, only: list[str] | None) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    jobs = [
        (benchmark, task, skilled)
        for benchmark in ("editeval", "pub")
        for task in manifest[benchmark]
        for skilled in (False, True)
        if only is None or f"{benchmark}-{task}" in only
    ]
    output.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manifest_path, output / "manifest.json")
    failures = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(run_batch, manifest, output, benchmark, task, skilled, timeout): (benchmark, task, skilled)
            for benchmark, task, skilled in jobs
        }
        for future in as_completed(futures):
            result = future.result()
            print(f"{result['benchmark']}-{result['task']} {result['mode']}: {result['status']}; skill_read={result['skill_read']}", flush=True)
            failures += result["status"] != "captured"
    if failures:
        raise RuntimeError(f"{failures} benchmark calls failed or did not use the intended skill condition")


def score(output: Path, bootstrap_replicates: int) -> None:
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    report = {"editeval": defaultdict(dict), "pub": defaultdict(dict)}
    pub_pairs = []
    edit_pairs = []
    edit_groups = []
    for benchmark in ("editeval", "pub"):
        for task, rows in manifest[benchmark].items():
            task_answers = {}
            for mode in ("baseline", "felicity"):
                prefix = output / mode / f"{benchmark}-{task}"
                meta_path = prefix.with_suffix(".meta.json")
                if not meta_path.is_file():
                    continue
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                try:
                    data = json.loads(prefix.with_suffix(".final.json").read_text(encoding="utf-8"))
                    answers = data["answers"]
                    if len(answers) != len(rows):
                        raise ValueError(f"expected {len(rows)} answers, got {len(answers)}")
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    report[benchmark][task][mode] = {"status": "invalid-output", "error": str(exc)}
                    continue
                if meta["status"] != "captured":
                    report[benchmark][task][mode] = {"status": meta["status"], "error": meta["error"]}
                    continue
                task_answers[mode] = answers
                if benchmark == "pub":
                    correct = [answer == row["answer_index"] for answer, row in zip(answers, rows)]
                    report[benchmark][task][mode] = {
                        "status": meta["status"], "correct": sum(correct), "total": len(rows),
                        "accuracy": sum(correct) / len(rows), "skill_read": meta["skill_read"],
                    }
                else:
                    from src.metrics.easse_sari import corpus_sari

                    sari = corpus_sari(
                        orig_sents=[row["input"] for row in rows],
                        sys_sents=answers,
                        refs_sents=[[row["reference"] for row in rows]],
                    )
                    report[benchmark][task][mode] = {
                        "status": meta["status"], "sari": sari, "total": len(rows),
                        "skill_read": meta["skill_read"],
                    }
            if set(task_answers) == {"baseline", "felicity"}:
                if benchmark == "pub":
                    for row, base, fel in zip(rows, task_answers["baseline"], task_answers["felicity"]):
                        pub_pairs.append((base == row["answer_index"], fel == row["answer_index"]))
                    report[benchmark][task]["paired"] = {
                        "felicity_only_correct": sum(fel and not base for base, fel in pub_pairs[-len(rows):]),
                        "baseline_only_correct": sum(base and not fel for base, fel in pub_pairs[-len(rows):]),
                    }
                else:
                    group = list(zip(rows, task_answers["baseline"], task_answers["felicity"]))
                    edit_groups.append(group)
                    edit_pairs.extend(group)

    report["summary"] = {}
    if pub_pairs:
        report["summary"]["pub"] = {
            "paired_items": len(pub_pairs),
            "baseline_correct": sum(base for base, _ in pub_pairs),
            "felicity_correct": sum(fel for _, fel in pub_pairs),
            "felicity_only_correct": sum(fel and not base for base, fel in pub_pairs),
            "baseline_only_correct": sum(base and not fel for base, fel in pub_pairs),
        }
    if edit_pairs:
        from src.metrics.easse_sari import corpus_sari

        inputs = [row["input"] for row, _, _ in edit_pairs]
        refs = [[row["reference"] for row, _, _ in edit_pairs]]
        report["summary"]["editeval"] = {
            "paired_items": len(edit_pairs),
            "original_sari": corpus_sari(inputs, inputs, refs),
            "baseline_sari": corpus_sari(inputs, [base for _, base, _ in edit_pairs], refs),
            "felicity_sari": corpus_sari(inputs, [fel for _, _, fel in edit_pairs], refs),
        }
        if bootstrap_replicates:
            rng = random.Random(793)
            differences = []
            for _ in range(bootstrap_replicates):
                sample = [group[rng.randrange(len(group))] for group in edit_groups for _ in group]
                sample_inputs = [row["input"] for row, _, _ in sample]
                sample_refs = [[row["reference"] for row, _, _ in sample]]
                differences.append(
                    corpus_sari(sample_inputs, [fel for _, _, fel in sample], sample_refs)
                    - corpus_sari(sample_inputs, [base for _, base, _ in sample], sample_refs)
                )
            differences.sort()
            report["summary"]["editeval"]["paired_bootstrap"] = {
                "replicates": bootstrap_replicates,
                "seed": 793,
                "stratified_by_task": True,
                "delta_sari_95_percentile_interval": [
                    differences[int(bootstrap_replicates * 0.025)],
                    differences[min(bootstrap_replicates - 1, int(bootstrap_replicates * 0.975))],
                ],
            }
    save_json(output / "scores.json", report)
    print(json.dumps(report, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run", "score"))
    parser.add_argument("--iterater-test", type=Path)
    parser.add_argument("--pub-dir", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--only", action="append")
    args = parser.parse_args()
    if args.action == "prepare":
        if not args.iterater_test or not args.pub_dir:
            parser.error("prepare requires --iterater-test and --pub-dir")
        prepare(args.iterater_test, args.pub_dir, args.out, args.count)
    elif args.action == "run":
        if not args.manifest:
            parser.error("run requires --manifest")
        run(args.manifest, args.out, args.timeout, args.workers, args.only)
    else:
        score(args.out, args.bootstrap)


if __name__ == "__main__":
    main()
