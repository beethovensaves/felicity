# Install Felicity

Install both skills from a release ZIP, or copy them from a source checkout. The optional Claude Code
rule is installed only when requested. Commands in the release section use downloaded files; source
commands use a `felicity/` checkout.

## Prerequisites

Plain text needs no additional software. Optional document support uses:

| Format | Requirement |
|---|---|
| DOCX, PPTX | Python 3 standard library |
| RTF, DOC | `textutil` on macOS |
| PDF | `pdftotext` from Poppler |
| Keynote | Export to PDF or PPTX |

On macOS, install Poppler with `brew install poppler`. On Debian or Ubuntu, use
`apt-get install poppler-utils`.

## Install from a release

Download the [Codex ZIP](https://github.com/beethovensaves/felicity/releases/latest/download/felicity-codex.zip),
[Claude Code ZIP](https://github.com/beethovensaves/felicity/releases/latest/download/felicity-claude-code.zip),
and [SHA256SUMS](https://github.com/beethovensaves/felicity/releases/latest/download/SHA256SUMS)
to the same directory. Check both downloaded archives there. On macOS:

```bash
shasum -a 256 -c SHA256SUMS
```

On Linux:

```bash
sha256sum -c SHA256SUMS
```

Then extract and install the package for your host from that directory:

```bash
# Codex
unzip felicity-codex.zip
python3 felicity-codex/install.py --scope user

# Claude Code
unzip felicity-claude-code.zip
python3 felicity-claude-code/install.py --scope user
```

Run only the two commands for the host you use. User scope installs the skills in `~/.agents/skills/`
for Codex or `~/.claude/skills/` for Claude Code. For one project, use
`--scope project --project /path/to/project`. Add `--replace` when updating; the installer backs up
the Felicity paths it replaces. It also checks each file against the ZIP's `checksums.sha256` before
writing to the destination.

For Claude Code, `--with-rule` also installs `felicity.md`. User scope puts this unfiltered rule in
`~/.claude/rules/`, where it applies across Claude Code projects. Project scope puts it in the
chosen project's `.claude/rules/`, where it applies within that project.

## Build from source

From the `felicity/` checkout, validate the source and build both ZIPs:

```bash
python3 scripts/check_package.py
shasum -a 256 -c MANIFEST.sha256
python3 scripts/build_packages.py
```

`MANIFEST.sha256` verifies the source checkout. It is not included in either release ZIP. The build
does not install anything. The manual copy commands below also run from the `felicity/` checkout.

## Codex

Personal installation:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R felicity-review felicity-write "$HOME/.agents/skills/"
```

For a project installation from this checkout:

```bash
felicity_project=/path/to/project
mkdir -p "$felicity_project/.agents/skills"
cp -R felicity-review felicity-write "$felicity_project/.agents/skills/"
```

The `agents/openai.yaml` files supply Codex display metadata. The runtime instructions remain in
`SKILL.md`.

## Claude Code

Personal installation:

```bash
mkdir -p ~/.claude/skills
cp -R felicity-review ~/.claude/skills/
cp -R felicity-write ~/.claude/skills/
```

Project installation:

```bash
felicity_project=/path/to/project
mkdir -p "$felicity_project/.claude/skills"
cp -R felicity-review felicity-write "$felicity_project/.claude/skills/"
```

To enable the optional rule:

```bash
mkdir -p ~/.claude/rules
cp rule/felicity.md ~/.claude/rules/
```

For a project-scoped rule, copy `rule/felicity.md` to that project's `.claude/rules/` directory.

## Kiro

Workspace installation:

```bash
mkdir -p .kiro/skills
cp -R /path/to/felicity/felicity-review .kiro/skills/
cp -R /path/to/felicity/felicity-write .kiro/skills/
```

For a global IDE or CLI installation, use `~/.kiro/skills/`.

The optional rule is a steering file:

```bash
mkdir -p .kiro/steering
cp /path/to/felicity/rule/felicity.md .kiro/steering/
```

Use workspace scope when the skill must be available on Kiro surfaces that do not load global
resources. Custom agents may need explicit skill and steering resources; see
[`HOST-NOTES.md`](HOST-NOTES.md).

## Updating an Existing Copy

Copying a folder onto an existing folder can retain deleted files from an older release. The host
package installer handles this with `--replace`, leaving timestamped backups. For a manual update,
replace the two exact Felicity directories:

```bash
rm -rf ~/.claude/skills/felicity-review ~/.claude/skills/felicity-write
cp -R felicity-review felicity-write ~/.claude/skills/
```

Use the equivalent skills root for Codex or Kiro. The manual command removes only the two named
Felicity install directories.

## Verify

For a Codex user installation, confirm that both skills contain their references:

```bash
test -r ~/.agents/skills/felicity-review/references/review-standard.md
test -r ~/.agents/skills/felicity-write/references/writing-standard.md
```

For a Claude Code user installation:

```bash
test -r ~/.claude/skills/felicity-review/references/review-standard.md
test -r ~/.claude/skills/felicity-write/references/writing-standard.md
python3 ~/.claude/skills/felicity-review/scripts/extract_text.py --help
```

Then ask Codex to use each skill:

```text
Use $felicity-review to review: "Latency rose after the cache change, so remove Redis."
Use $felicity-write to rewrite: "We leverage a robust solution to unlock seamless workflows."
```

In Claude Code, use its slash syntax:

```text
/felicity-review Review: "Latency rose after the cache change, so remove Redis."
/felicity-write Rewrite: "We leverage a robust solution to unlock seamless workflows."
```

The first should question the unsupported conclusion. The second should ask for a concrete product
fact if the sentence offers only generic praise.

## More requests

In Codex:

```text
Use $felicity-review to review path/to/deck.pptx.
Use $felicity-review to critique this system prompt.
Use $felicity-write to revise docs/design.md in place.
Use $felicity-write to draft a short project update for leadership.
```

In Claude Code, replace `$felicity-review` and `$felicity-write` with `/felicity-review` and
`/felicity-write` at the start of the corresponding request.

Review never edits. Write edits only when the request asks for file changes.
