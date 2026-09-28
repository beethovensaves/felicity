#!/usr/bin/env python3
"""Validate the Felicity distribution using only the Python standard library."""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "felicity-review": {
        "reference": "references/review-standard.md",
        "default_prompt": "$felicity-review",
    },
    "felicity-write": {
        "reference": "references/writing-standard.md",
        "extra_reference": "references/anti-slop.md",
        "default_prompt": "$felicity-write",
    },
}
ALLOWED_FRONTMATTER = {"name", "description"}
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError("missing or malformed YAML frontmatter")

    lines = match.group(1).splitlines()
    keys: list[str] = []
    values: dict[str, str] = {}
    current: str | None = None
    folded: list[str] = []

    def finish_folded() -> None:
        nonlocal current, folded
        if current is not None and folded:
            values[current] = " ".join(part.strip() for part in folded).strip()
        current = None
        folded = []

    for line in lines:
        key_match = re.match(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$", line)
        if key_match:
            finish_folded()
            key, raw_value = key_match.groups()
            keys.append(key)
            raw_value = (raw_value or "").strip()
            if raw_value in {">", ">-", "|", "|-"}:
                current = key
            else:
                values[key] = raw_value.strip("\"'")
            continue
        if current is None or not line.startswith((" ", "\t")):
            raise ValueError(f"cannot parse frontmatter line: {line!r}")
        folded.append(line)

    finish_folded()
    values["_keys"] = ",".join(keys)
    return values


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def package_files() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if (
            relative.name in {".DS_Store", "MANIFEST.sha256"}
            or relative.parts[0] == ".git"
            or relative.parts[0] == "dist"
            or relative.parts[:2] == ("evals", "results")
            or "__pycache__" in relative.parts
        ):
            continue
        files[str(relative)] = path
    return files


def validate_manifest() -> list[str]:
    errors: list[str] = []
    path = ROOT / "MANIFEST.sha256"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"MANIFEST.sha256: {exc}"]
    listed: set[str] = set()
    for number, line in enumerate(lines, start=1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.append(f"MANIFEST.sha256:{number}: invalid entry")
            continue
        expected, relative = match.groups()
        if relative in listed:
            errors.append(f"MANIFEST.sha256:{number}: duplicate {relative}")
            continue
        listed.add(relative)
        file = (ROOT / relative).resolve()
        if not file.is_relative_to(ROOT) or not file.is_file():
            errors.append(f"MANIFEST.sha256:{number}: missing or unsafe file {relative}")
        elif sha256(file) != expected:
            errors.append(f"MANIFEST.sha256:{number}: checksum mismatch {relative}")
    for relative in sorted(package_files().keys() - listed):
        errors.append(f"MANIFEST.sha256: unlisted file {relative}")
    return errors


def local_markdown_links(path: Path) -> list[str]:
    broken: list[str] = []
    text = path.read_text(encoding="utf-8")
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.strip().strip("<>")
        if (
            not target
            or target.startswith(("#", "http://", "https://", "mailto:"))
        ):
            continue
        relative = target.split("#", 1)[0]
        if not (path.parent / relative).resolve().exists():
            broken.append(target)
    return broken


def validate() -> list[str]:
    errors: list[str] = []

    errors.extend(validate_manifest())
    if not (ROOT / "README.md").is_file():
        errors.append("missing README.md")

    for name, expected in SKILLS.items():
        folder = ROOT / name
        skill_md = folder / "SKILL.md"
        try:
            frontmatter = parse_frontmatter(skill_md)
        except (OSError, ValueError) as exc:
            errors.append(f"{skill_md.relative_to(ROOT)}: {exc}")
            continue

        keys = set(frontmatter.pop("_keys", "").split(","))
        if keys != ALLOWED_FRONTMATTER:
            errors.append(
                f"{skill_md.relative_to(ROOT)}: frontmatter keys are {sorted(keys)}, "
                f"expected {sorted(ALLOWED_FRONTMATTER)}"
            )
        if frontmatter.get("name") != name:
            errors.append(
                f"{skill_md.relative_to(ROOT)}: name does not match folder"
            )
        description = frontmatter.get("description", "")
        if not description or len(description) > 1024:
            errors.append(
                f"{skill_md.relative_to(ROOT)}: description length is "
                f"{len(description)}, expected 1-1024"
            )
        if "<" in description or ">" in description:
            errors.append(
                f"{skill_md.relative_to(ROOT)}: description contains angle brackets"
            )
        if len(skill_md.read_text(encoding="utf-8").splitlines()) >= 500:
            errors.append(f"{skill_md.relative_to(ROOT)}: body exceeds 499 lines")

        required = [
            folder / expected["reference"],
            folder / "scripts/extract_text.py",
            folder / "agents/openai.yaml",
        ]
        if "extra_reference" in expected:
            required.append(folder / expected["extra_reference"])
        for required_path in required:
            if not required_path.is_file():
                errors.append(f"missing {required_path.relative_to(ROOT)}")

        prompt_file = folder / "agents/openai.yaml"
        if prompt_file.is_file():
            prompt_text = prompt_file.read_text(encoding="utf-8")
            if expected["default_prompt"] not in prompt_text:
                errors.append(
                    f"{prompt_file.relative_to(ROOT)}: default prompt does not name skill"
                )

        extractor = folder / "scripts/extract_text.py"
        if extractor.is_file():
            try:
                compile(
                    extractor.read_text(encoding="utf-8"),
                    str(extractor),
                    "exec",
                )
            except SyntaxError as exc:
                errors.append(f"{extractor.relative_to(ROOT)}: {exc}")
            result = subprocess.run(
                [sys.executable, str(extractor), "--help"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode != 0:
                errors.append(
                    f"{extractor.relative_to(ROOT)}: --help failed: "
                    f"{result.stderr.strip()}"
                )

        for path in folder.rglob("*"):
            if path.is_symlink():
                errors.append(f"{path.relative_to(ROOT)}: skill contains a symlink")

    review_extractor = ROOT / "felicity-review/scripts/extract_text.py"
    write_extractor = ROOT / "felicity-write/scripts/extract_text.py"
    if review_extractor.is_file() and write_extractor.is_file():
        if sha256(review_extractor) != sha256(write_extractor):
            errors.append("the two extractor copies differ")

    for path in ROOT.rglob("*.md"):
        parts = path.relative_to(ROOT).parts
        if parts[0] == "dist" or parts[:2] == ("evals", "results"):
            continue
        for target in local_markdown_links(path):
            errors.append(f"{path.relative_to(ROOT)}: broken link {target!r}")

    for name in (
        "scripts/build_packages.py", "scripts/install_package.py", "scripts/run_evals.py",
        "scripts/summarize_evals.py",
    ):
        path = ROOT / name
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (OSError, SyntaxError) as exc:
            errors.append(f"{name}: {exc}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Felicity package validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Felicity package validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
