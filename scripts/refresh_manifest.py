#!/usr/bin/env python3
"""Regenerate MANIFEST.sha256 for the Felicity source package."""

from __future__ import annotations

from check_package import ROOT, package_files, sha256


def main() -> int:
    lines = [f"{sha256(path)}  {name}" for name, path in sorted(package_files().items())]
    (ROOT / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines)} checksums.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
