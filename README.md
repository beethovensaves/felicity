# Felicity

Felicity is a pair of writing skills for Codex and Claude Code grounded in linguistics and
pragmatics. It treats writing as an action between a writer and a reader: a sentence can be true yet
imply too much, a request can sound optional, and an edit can erase the voice that made the original
work. Felicity checks those effects before polishing the surface.

Its approach draws on speech acts, common ground, information flow, and
[Grice's cooperative principle](https://web.stanford.edu/class/psych205/papers/Grice-1975.pdf).
The principles guide judgment in context; they are not a word blacklist or a numeric score.

| Skill | Use it for | What it returns |
| --- | --- | --- |
| [`felicity-review`](felicity-review/SKILL.md) | Review, critique, audit, or proofread | Prioritized findings with reader consequences and concrete fixes. It does not edit the source. |
| [`felicity-write`](felicity-write/SKILL.md) | Draft, rewrite, tighten, polish, or de-slop | Finished prose or an in-place edit when requested. It preserves supported claims and the author's voice. |

Review keeps a consequential finding threshold: it flags a problem when a likely reader could
misunderstand, take the wrong action, lose trust, or expend avoidable effort. A preference about style
alone is not a finding. Write ends with a concentrated check for stock openings, inflated claims,
mechanical contrasts, and other formulaic moves. It changes them when they weaken the text, while
keeping useful idiom and technical language.

In an [observed Codex run](evals/RESULTS.md), a review of “Latency rose after the cache change, so
we should remove Redis” identified the unsupported causal leap and recommended isolating the cause
before deciding. A separate run found no issue with an update that clearly limited completion to
staging. The [complete answers and manual grades](evals/RESULTS.md) are available in the repository.

## Install

Download the package for your host from the [latest release](https://github.com/beethovensaves/felicity/releases/latest):

- [Codex ZIP](https://github.com/beethovensaves/felicity/releases/latest/download/felicity-codex.zip)
- [Claude Code ZIP](https://github.com/beethovensaves/felicity/releases/latest/download/felicity-claude-code.zip)
- [SHA256 checksums](https://github.com/beethovensaves/felicity/releases/latest/download/SHA256SUMS)

If you download all three files together, check the archives with `shasum -a 256 -c SHA256SUMS`
on macOS or `sha256sum -c SHA256SUMS` on Linux.
Extract the ZIP for your host, then run its installer with Python 3:

```bash
# Codex
unzip felicity-codex.zip
python3 felicity-codex/install.py --scope user

# Claude Code
unzip felicity-claude-code.zip
python3 felicity-claude-code/install.py --scope user
```

For a project installation, use `--scope project --project /path/to/project`. Add `--replace` to
update an existing Felicity installation; the installer backs up the Felicity paths it replaces.
The Claude Code package also supports `--with-rule`. With user scope, it installs an unfiltered rule
in `~/.claude/rules/` that applies across Claude Code projects; with project scope, the rule applies
within that project. The installer checks every packaged file against its checksum list before
writing to the destination. See [INSTALL.md](INSTALL.md) for download, source, and document details.

## Use

In Codex:

```text
Use $felicity-review to review this status update for consequential problems.
Use $felicity-write to revise README.md in place while preserving its claims and voice.
```

In Claude Code:

```text
/felicity-review Review this status update for consequential problems.
/felicity-write Revise README.md in place while preserving its claims and voice.
```

The skills can read plain text, DOCX, PPTX, RTF, legacy DOC, and text-layer PDFs. DOCX and PPTX
extraction use Python's standard library; PDF needs `pdftotext`, and RTF or legacy DOC needs macOS
`textutil`. Extraction cannot read meaning carried only by images, charts, or layout. Editing a
document format in place requires a format-aware editor supplied by the host.

## Verify and evaluate

From the source checkout:

```bash
python3 scripts/check_package.py
python3 scripts/build_packages.py
python3 scripts/run_evals.py --list
```

The [behavior cases](evals/README.md) cover claim drift, speech-act force, shared context, review
restraint, voice preservation, technical senses, and formulaic writing. The [published sample](evals/RESULTS.md)
contains three manually graded Codex runs. It does not establish overall quality or Claude Code
behavior. Package validation checks structure and checksums, not writing quality.

The skills and build scripts are in this repository. [Host notes](HOST-NOTES.md) explain discovery
paths and optional rules. Felicity is released under the [MIT License](LICENSE).
