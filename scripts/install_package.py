#!/usr/bin/env python3
"""Install an extracted Felicity package into Codex or Claude Code."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
SKILLS = ("felicity-review", "felicity-write")
HOSTS = {
    "codex": (".agents", "skills"),
    "claude": (".claude", "skills"),
}


def verify_package() -> str:
    host = (PACKAGE / "host.txt").read_text(encoding="utf-8").strip()
    if host not in HOSTS:
        raise ValueError("host.txt must say codex or claude")
    manifest = PACKAGE / "checksums.sha256"
    entries: set[str] = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if len(line) < 67 or line[64:66] != "  ":
            raise ValueError("invalid checksum line")
        expected, relative = line[:64], line[66:]
        if any(character not in "0123456789abcdef" for character in expected):
            raise ValueError("invalid checksum")
        path = PACKAGE / relative
        if relative in entries or path.is_symlink() or not path.resolve().is_relative_to(PACKAGE):
            raise ValueError(f"unsafe or duplicate package path: {relative}")
        entries.add(relative)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"missing or changed package file: {relative}")
    for name in SKILLS:
        if f"skills/{name}/SKILL.md" not in entries:
            raise ValueError(f"missing packaged skill: {name}")
    if host == "claude" and "rule/felicity.md" not in entries:
        raise ValueError("missing optional Claude rule")
    actual = {
        str(path.relative_to(PACKAGE))
        for path in PACKAGE.rglob("*")
        if path.is_file() or path.is_symlink()
    }
    expected = entries | {"checksums.sha256"}
    if actual != expected:
        raise ValueError(
            f"package file list differs from checksums: missing={sorted(expected - actual)}, "
            f"unlisted={sorted(actual - expected)}"
        )
    return host


def destination(host: str, args: argparse.Namespace) -> Path:
    if args.dest:
        return args.dest.expanduser().resolve()
    folder, skills = HOSTS[host]
    if args.scope == "user":
        if args.project:
            raise ValueError("--project requires --scope project")
        return Path.home() / folder / skills
    if not args.project:
        raise ValueError("--scope project requires --project PATH")
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"project directory does not exist: {project}")
    return project / folder / skills


def install(host: str, skills_dir: Path, replace: bool, with_rule: bool) -> list[Path]:
    if with_rule and host != "claude":
        raise ValueError("--with-rule is only available for Claude Code")
    payload: list[tuple[Path, Path]] = [
        (PACKAGE / "skills" / name, skills_dir / name) for name in SKILLS
    ]
    if with_rule:
        payload.append((PACKAGE / "rule/felicity.md", skills_dir.parent / "rules/felicity.md"))
    existing = [target for _, target in payload if target.exists() or target.is_symlink()]
    if existing and not replace:
        raise ValueError(
            "already installed: " + ", ".join(str(path) for path in existing)
            + "; use --replace to back up and replace these exact paths"
        )

    skills_dir.mkdir(parents=True, exist_ok=True)
    staged_root = Path(tempfile.mkdtemp(prefix=".felicity-stage-", dir=skills_dir.parent))
    backups: list[tuple[Path, Path]] = []
    installed: list[Path] = []
    try:
        staged: list[tuple[Path, Path]] = []
        for source, target in payload:
            stage = staged_root / target.name
            if source.is_dir():
                shutil.copytree(source, stage)
            else:
                shutil.copy2(source, stage)
            staged.append((stage, target))

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        for _, target in staged:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() or target.is_symlink():
                backup = target.with_name(f"{target.name}.felicity-backup-{stamp}")
                if backup.exists():
                    raise ValueError(f"backup path already exists: {backup}")
                os.replace(target, backup)
                backups.append((backup, target))
        for stage, target in staged:
            os.replace(stage, target)
            installed.append(target)
    except Exception:
        for target in reversed(installed):
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
        for backup, target in reversed(backups):
            os.replace(backup, target)
        raise
    finally:
        shutil.rmtree(staged_root, ignore_errors=True)
    return installed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--project", type=Path)
    parser.add_argument("--dest", type=Path, help="install into an exact skills directory")
    parser.add_argument("--replace", action="store_true", help="back up and replace prior copies")
    parser.add_argument("--with-rule", action="store_true", help="install the optional Claude rule")
    args = parser.parse_args()
    try:
        host = verify_package()
        target = destination(host, args)
        installed = install(host, target, args.replace, args.with_rule)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    for path in installed:
        print(f"Installed {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
