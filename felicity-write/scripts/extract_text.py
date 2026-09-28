#!/usr/bin/env python3
"""Extract reviewable text from common document formats without modifying them."""

from __future__ import annotations

import argparse
import posixpath
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET


REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE_REL_NS = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
)
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
PRESENTATION_NS = (
    "http://schemas.openxmlformats.org/presentationml/2006/main"
)
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


class ExtractionError(RuntimeError):
    """Raised when a document cannot be read reliably."""


def _xml(zf: zipfile.ZipFile, member: str) -> ET.Element:
    try:
        return ET.fromstring(zf.read(member))
    except KeyError as exc:
        raise ExtractionError(f"archive is missing {member}") from exc
    except ET.ParseError as exc:
        raise ExtractionError(f"invalid XML in {member}: {exc}") from exc


def _paragraph_text(paragraph: ET.Element, text_tag: str) -> str:
    parts: list[str] = []
    for node in paragraph.iter():
        if node.tag == text_tag and node.text:
            parts.append(node.text)
        elif node.tag.endswith("}tab"):
            parts.append("\t")
        elif node.tag.endswith("}br") or node.tag.endswith("}cr"):
            parts.append("\n")
    return "".join(parts).strip()


def _extract_docx(path: Path) -> str:
    paragraph_tag = f"{{{WORD_NS}}}p"
    text_tag = f"{{{WORD_NS}}}t"

    try:
        with zipfile.ZipFile(path) as zf:
            root = _xml(zf, "word/document.xml")
    except zipfile.BadZipFile as exc:
        raise ExtractionError("not a valid DOCX archive") from exc

    paragraphs = [
        text
        for paragraph in root.iter(paragraph_tag)
        if (text := _paragraph_text(paragraph, text_tag))
    ]
    if not paragraphs:
        raise ExtractionError("DOCX contains no extractable paragraph text")
    return "\n".join(paragraphs)


def _relationships(zf: zipfile.ZipFile, member: str) -> dict[str, tuple[str, str]]:
    root = _xml(zf, member)
    relationships: dict[str, tuple[str, str]] = {}
    for rel in root.findall(f"{{{REL_NS}}}Relationship"):
        rel_id = rel.get("Id")
        target = rel.get("Target")
        rel_type = rel.get("Type", "")
        if rel_id and target:
            relationships[rel_id] = (target, rel_type)
    return relationships


def _resolve_part(source_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(
        posixpath.join(str(PurePosixPath(source_part).parent), target)
    )


def _rels_part(source_part: str) -> str:
    part = PurePosixPath(source_part)
    return str(part.parent / "_rels" / f"{part.name}.rels")


def _drawing_paragraphs(root: ET.Element) -> list[str]:
    paragraph_tag = f"{{{DRAWING_NS}}}p"
    text_tag = f"{{{DRAWING_NS}}}t"
    return [
        text
        for paragraph in root.iter(paragraph_tag)
        if (text := _paragraph_text(paragraph, text_tag))
    ]


def _slide_parts(zf: zipfile.ZipFile) -> list[str]:
    presentation_part = "ppt/presentation.xml"
    root = _xml(zf, presentation_part)
    relationships = _relationships(zf, _rels_part(presentation_part))

    slide_ids = root.find(f".//{{{PRESENTATION_NS}}}sldIdLst")
    if slide_ids is None:
        raise ExtractionError("presentation.xml has no slide list")

    parts: list[str] = []
    rel_key = f"{{{OFFICE_REL_NS}}}id"
    for slide_id in slide_ids.findall(f"{{{PRESENTATION_NS}}}sldId"):
        rel_id = slide_id.get(rel_key)
        if not rel_id or rel_id not in relationships:
            raise ExtractionError(f"cannot resolve slide relationship {rel_id!r}")
        target, _ = relationships[rel_id]
        parts.append(_resolve_part(presentation_part, target))
    return parts


def _notes_part(zf: zipfile.ZipFile, slide_part: str) -> str | None:
    rels_member = _rels_part(slide_part)
    if rels_member not in zf.namelist():
        return None
    for target, rel_type in _relationships(zf, rels_member).values():
        if rel_type.endswith("/notesSlide"):
            return _resolve_part(slide_part, target)
    return None


def _extract_pptx(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as zf:
            blocks: list[str] = []
            for number, slide_part in enumerate(_slide_parts(zf), start=1):
                slide_lines = _drawing_paragraphs(_xml(zf, slide_part))
                blocks.append(f"## Slide {number}")
                blocks.extend(slide_lines or ["[No extractable on-slide text]"])

                notes_part = _notes_part(zf, slide_part)
                if notes_part:
                    note_lines = _drawing_paragraphs(_xml(zf, notes_part))
                    if note_lines:
                        blocks.append("### Speaker notes")
                        blocks.extend(note_lines)
    except zipfile.BadZipFile as exc:
        raise ExtractionError("not a valid PPTX archive") from exc

    if not blocks:
        raise ExtractionError("PPTX contains no slides")
    return "\n".join(blocks)


def _run_converter(command: list[str], label: str) -> str:
    executable = command[0]
    if shutil.which(executable) is None:
        raise ExtractionError(f"{label} requires {executable}, but it is not installed")

    result = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ExtractionError(f"{label} failed: {detail or 'unknown error'}")

    text = result.stdout.decode("utf-8", errors="replace").strip()
    if not text:
        raise ExtractionError(f"{label} returned no text")
    return text


def extract(path: Path) -> str:
    if not path.is_file():
        raise ExtractionError("file does not exist")

    suffix = path.suffix.lower()
    if suffix == ".docx":
        return _extract_docx(path)
    if suffix == ".pptx":
        return _extract_pptx(path)
    if suffix in {".doc", ".rtf"}:
        return _run_converter(
            ["textutil", "-convert", "txt", "-stdout", str(path)],
            f"{suffix[1:].upper()} extraction",
        )
    if suffix == ".pdf":
        return _run_converter(
            ["pdftotext", "-layout", str(path), "-"],
            "PDF extraction",
        )
    if suffix == ".key":
        raise ExtractionError("Keynote files require a PDF or PPTX export")

    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace").strip()
    except OSError as exc:
        raise ExtractionError(f"could not read text: {exc}") from exc
    if not text:
        raise ExtractionError("file contains no text")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract text from documents without modifying them."
    )
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    failed = False
    multiple = len(args.paths) > 1
    for path in args.paths:
        try:
            text = extract(path)
        except ExtractionError as exc:
            print(f"error: {path}: {exc}", file=sys.stderr)
            failed = True
            continue

        if multiple:
            print(f"# File: {path}")
        print(text)
        if multiple and path != args.paths[-1]:
            print()

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
