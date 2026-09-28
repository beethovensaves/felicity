#!/usr/bin/env python3
"""Build reproducible Codex and Claude Code ZIP packages for Felicity."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("felicity-review", "felicity-write")
HOSTS = {"codex": "felicity-codex", "claude": "felicity-claude-code"}


def package_readme(host: str) -> bytes:
    product = "Codex" if host == "codex" else "Claude Code"
    location = "~/.agents/skills/" if host == "codex" else "~/.claude/skills/"
    project = ".agents/skills/" if host == "codex" else ".claude/skills/"
    rule = (
        "\nFor the optional always-on Claude rule, add `--with-rule`. It installs to "
        "`~/.claude/rules/` or the project's `.claude/rules/`.\n"
        if host == "claude" else ""
    )
    return (
        f"# Felicity for {product}\n\n"
        "This package installs `felicity-review` and `felicity-write`. Python 3 is required for the\n"
        "installer and document extraction. Review the skills before installation.\n\n"
        "From this extracted package directory:\n\n"
        "```bash\npython3 install.py --scope user\n"
        "python3 install.py --scope project --project /path/to/project\n```\n\n"
        f"Personal skills go to `{location}`; project skills go to `{project}`.\n"
        "If an older Felicity copy exists, add `--replace`. The installer keeps timestamped backups\n"
        "of only the paths it replaces. Use `--dest /path/to/skills` for a custom skills directory.\n"
        + rule
        + "\nThe extractor reads DOCX, PPTX, RTF, DOC, and text-layer PDF files. PDF needs `pdftotext`;\n"
        "RTF and legacy DOC need macOS `textutil`. It does not edit those formats.\n"
    ).encode("utf-8")


def payload(host: str) -> dict[str, bytes]:
    files = {
        "README.md": package_readme(host),
        "host.txt": (host + "\n").encode("utf-8"),
        "install.py": (ROOT / "scripts/install_package.py").read_bytes(),
    }
    for name in SKILLS:
        folder = ROOT / name
        for path in sorted(folder.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"skill contains a symlink: {path}")
            if path.is_file() and "__pycache__" not in path.parts:
                files[str(Path("skills") / name / path.relative_to(folder))] = path.read_bytes()
    if host == "claude":
        files["rule/felicity.md"] = (ROOT / "rule/felicity.md").read_bytes()
    checksums = [
        f"{hashlib.sha256(content).hexdigest()}  {name}"
        for name, content in sorted(files.items())
    ]
    files["checksums.sha256"] = ("\n".join(checksums) + "\n").encode("utf-8")
    return files


def write_zip(path: Path, folder: str, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative, content in sorted(files.items()):
            entry = zipfile.ZipInfo(f"{folder}/{relative}", date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_package.py")],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if result.returncode:
        parser.error(result.stderr.strip() or "package validation failed")
    out = args.out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    for host, folder in HOSTS.items():
        path = out / f"{folder}.zip"
        write_zip(path, folder, payload(host))
        print(f"Built {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
