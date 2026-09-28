# Host Notes

Felicity keeps portable behavior in `SKILL.md` and host-specific metadata outside it.

## Portable Skill Contract

Each skill contains:

- `SKILL.md` with only `name` and `description` frontmatter;
- a local execution reference;
- a local document-extraction script.

The folder is self-contained. A host may ignore files it does not recognize without affecting the
runtime instructions.

## Codex

`agents/openai.yaml` provides the display name, short description, and default prompt shown by Codex.
It does not replace `SKILL.md`.

Current personal location:

```text
$HOME/.agents/skills/<skill-name>/
```

Repository skills live under `.agents/skills/<skill-name>/`. The Codex ZIP contains both skills and
an installer for those locations.

Invocation examples use `$felicity-review` and `$felicity-write`.

## Claude Code

Typical locations:

```text
~/.claude/skills/<skill-name>/
.claude/skills/<skill-name>/
```

Claude Code also supports persistent rule files under user or project `.claude/rules/` directories.
The optional Felicity rule has no path filter and therefore applies broadly.

The Claude Code ZIP installs both skills. Its installer adds the always-on rule only when run with
`--with-rule`.

Invoke the skills explicitly as `/felicity-review` and `/felicity-write`. The `$` prefix used by
Codex is not Claude Code's invocation syntax.

This release does not use Claude-only frontmatter such as `disable-model-invocation` or
`argument-hint`. Whether a skill matches implicitly is a host or user setting, not a second behavior
hidden in the portable skill.

## Kiro

Typical locations:

```text
~/.kiro/skills/<skill-name>/
.kiro/skills/<skill-name>/
```

The optional rule belongs under `.kiro/steering/` or `~/.kiro/steering/`. Workspace resources are the
safer choice when the same setup must work across IDE, CLI, web, and mobile surfaces.

Kiro custom agents do not necessarily inherit all workspace skills or steering. Add the relevant
skill and steering resources to the custom-agent configuration when Felicity is missing there.

## Document Extraction

The bundled extractor behaves the same on every host that can run Python 3:

```bash
python3 scripts/extract_text.py document.docx
python3 scripts/extract_text.py deck.pptx
```

DOCX and PPTX extraction use only the standard library. RTF and legacy DOC depend on macOS
`textutil`. PDF depends on `pdftotext`. If a host denies command execution, provide pasted text or a
plain-text export.

The PPTX path resolves slide relationships from `presentation.xml`, so slide 10 does not sort before
slide 2. It also follows each slide's relationship to its speaker notes.

## Rules and Automatic Hooks

The always-on rule is optional. It helps with first drafts but should not replace a deliberate review
of consequential text.

Automatic review hooks are host configuration, not part of either skill. Keep hook setup outside the
portable package so a review cannot unexpectedly run after every write. When adding a hook, scope it
to the files that warrant the latency and output.

## Vendor Documentation

Host behavior changes independently of this package. Check current vendor documentation before
relying on discovery paths, implicit invocation, global-resource support, or custom-agent inheritance:

- Agent Skills specification: <https://agentskills.io/specification>
- Claude Code skills: <https://code.claude.com/docs/en/skills>
- Kiro skills: <https://kiro.dev/docs/skills/>
