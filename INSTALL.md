# Install Felicity

Install both skills from a host package, or copy them from the source tree. The always-on rule is
optional. Download the [Codex](https://github.com/beethovensaves/felicity/releases/latest/download/felicity-codex.zip)
or [Claude Code](https://github.com/beethovensaves/felicity/releases/latest/download/felicity-claude-code.zip)
ZIP from the latest release. Source-copy commands below assume you are in the directory containing
the `felicity/` checkout.

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

## Host Packages

To build the ZIPs yourself, enter the `felicity/` source directory and run:

```bash
python3 scripts/refresh_manifest.py
python3 scripts/build_packages.py
```

For Codex, run these from the `felicity/` source directory:

```bash
unzip dist/felicity-codex.zip -d /tmp/felicity-install
cd /tmp/felicity-install/felicity-codex
python3 install.py --scope user
```

For Claude Code, extract `dist/felicity-claude-code.zip` and run the same command inside its
`felicity-claude-code/` directory. Use `--scope project --project /path/to/project` for a project
installation. Add `--replace` when updating an existing copy; the installer backs up only the
specific Felicity paths it replaces. Claude Code's optional rule requires `--with-rule`.

The package installer checks every payload file against `checksums.sha256` before it writes to the
destination. It does not install anything during the build.

## Codex

Personal installation:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R felicity/felicity-review felicity/felicity-write "$HOME/.agents/skills/"
```

For a project installation, copy the two folders into the project's `.agents/skills/` directory.

The `agents/openai.yaml` files supply Codex display metadata. The runtime instructions remain in
`SKILL.md`.

## Claude Code

Personal installation:

```bash
mkdir -p ~/.claude/skills
cp -R felicity/felicity-review ~/.claude/skills/
cp -R felicity/felicity-write ~/.claude/skills/
```

Project installation:

```bash
mkdir -p .claude/skills
cp -R /path/to/felicity/felicity-review .claude/skills/
cp -R /path/to/felicity/felicity-write .claude/skills/
```

To enable the optional rule:

```bash
mkdir -p ~/.claude/rules
cp felicity/rule/felicity.md ~/.claude/rules/
```

Use `.claude/rules/` instead for a project-scoped rule.

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
cp -R felicity/felicity-review felicity/felicity-write ~/.claude/skills/
```

Use the equivalent skills root for Codex or Kiro. The manual command removes only the two named
Felicity install directories.

## Verify

Confirm that each installed skill contains its own files:

```bash
test -r ~/.claude/skills/felicity-review/references/review-standard.md
test -r ~/.claude/skills/felicity-write/references/writing-standard.md
python3 ~/.claude/skills/felicity-review/scripts/extract_text.py --help
```

To verify an extracted release before installation, run these from the `felicity/` directory:

```bash
python3 scripts/check_package.py
shasum -a 256 -c MANIFEST.sha256
```

Then ask the host to use each skill:

```text
Use $felicity-review to review: "Latency rose after the cache change, so remove Redis."
Use $felicity-write to rewrite: "We leverage a robust solution to unlock seamless workflows."
```

The first should question the unsupported conclusion. The second should remove generic claims
without inventing a specific benefit.

## Use

```text
Use $felicity-review to review path/to/deck.pptx.
Use $felicity-review to critique this system prompt.
Use $felicity-write to revise docs/design.md in place.
Use $felicity-write to draft a short project update for leadership.
```

Review never edits. Write edits only when the request asks for file changes.
