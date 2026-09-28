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

For example, a review of “Latency rose after the cache change, so we should remove Redis” should
question the causal leap. A rewrite of “We leverage a robust solution to unlock seamless workflows”
should remove unsupported praise without inventing a product benefit.

## Install

Download the package for your host from the [latest release](https://github.com/beethovensaves/felicity/releases/latest):

- [Codex ZIP](https://github.com/beethovensaves/felicity/releases/latest/download/felicity-codex.zip)
- [Claude Code ZIP](https://github.com/beethovensaves/felicity/releases/latest/download/felicity-claude-code.zip)
- [SHA256 checksums](https://github.com/beethovensaves/felicity/releases/latest/download/SHA256SUMS)

If you download all three files together, run `shasum -a 256 -c SHA256SUMS` to check the archives.
Extract one ZIP and run its installer with Python 3:

```bash
# Inside the directory where you extracted the Codex ZIP:
python3 felicity-codex/install.py --scope user

# Or, for the Claude Code ZIP:
python3 felicity-claude-code/install.py --scope user
```

For a project installation, use `--scope project --project /path/to/project`. Add `--replace` to
update an existing Felicity installation; the installer backs up the Felicity paths it replaces.
The Claude Code package also supports `--with-rule` for an optional rule that applies to prose work
beyond explicit skill calls. The installer checks every packaged file against its checksum list
before writing to the destination. See [INSTALL.md](INSTALL.md) for source installs, supported hosts,
document dependencies, and verification commands.

## Use

```text
Use $felicity-review to review this status update for consequential problems.
Use $felicity-write to revise README.md in place while preserving its claims and voice.
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
restraint, voice preservation, technical senses, and formulaic writing. They provide a way to
compare live Codex or Claude Code outputs; no live-model scores are published with this release.
Package validation checks structure and checksums, not writing quality.

The skills and build scripts are in this repository. [Host notes](HOST-NOTES.md) explain discovery
paths and optional rules. Felicity is released under the [MIT License](LICENSE).
