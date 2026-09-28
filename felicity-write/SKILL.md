---
name: felicity-write
description: >-
  Drafts, rewrites, and edits clear, natural prose while preserving meaning and calibrating claims.
  Use when the user asks to write, draft, rewrite, revise, tighten, polish, simplify, de-slop, or
  apply editorial changes to an email, post, report, deck, README, prompt, system prompt, tool
  description, or model response. Can read text, DOCX, PPTX, RTF, DOC, and text-layer PDFs. Edits
  files when explicitly requested and a suitable editor is available; otherwise returns finished
  text. Do not use for critique-only requests; use felicity-review to report findings without
  rewriting.
---

# Felicity Write

Produce the requested text, then revise it silently before returning it. Preserve the author's
meaning and voice unless the user asks to change either.

## Workflow

### 1. Read the request

Identify:

- the source, if this is a rewrite;
- the intended reader;
- the result the text must achieve;
- explicit constraints on length, format, tone, facts, and terminology;
- whether the user asked for an in-place file edit or a draft in chat.

Infer ordinary defaults from the genre and context. Ask a question only when a missing answer would
materially change the result. Do not ask for confirmation when the request, target, and intent are
already clear.

### 2. Read the source

Read plain-text and source files directly. For `.docx`, `.pptx`, `.rtf`, `.doc`, or `.pdf`, run:

```bash
python3 scripts/extract_text.py <path>
```

Resolve the script from this skill's directory. It writes extracted text to stdout and does not
modify the source. PDF extraction requires `pdftotext`.

The extractor does not edit or preserve the formatting of DOCX, PPTX, RTF, DOC, or PDF files. For
an in-place edit to one of these formats, use an available format-aware editor. If none is
available, return revised text and say the source file was not changed.

If extraction fails or returns no useful text, name the file and failed step, then ask for a text or
PDF export. Never rewrite a document you did not read.

Extraction does not reveal meaning carried only by images, charts, or layout. Inspect a rendering
when those elements matter and the host can show one; otherwise state the text-only rewrite scope.

### 3. Load the standard

Read [`references/writing-standard.md`](references/writing-standard.md) before drafting. Apply the
sections relevant to the genre; do not expose the internal checklist to the reader.

### 4. Draft or edit

Write the text the reader needs.

For a rewrite:

- notice the author's vocabulary, cadence, humor, uncertainty, and level of polish before editing;
- make the smallest change that solves the reader's problem; keep strong lines and intentional
  irregularity;
- preserve a useful progression or detour unless it hides the point or the user asks for a new one;
- preserve claims, citations, proper nouns, technical terms, IDs, and commitments;
- preserve the source's factual, causal, temporal, and evaluative claims exactly in substance;
- do not add facts, motives, inevitability, causal links, or stronger conclusions, even when they
  seem like obvious connective tissue;
- retain intentional voice and warmth;
- resolve ambiguity only when the intended meaning is supported by context;
- flag a source contradiction instead of silently choosing one version.

For new text:

- do not invent evidence, metrics, dates, owners, tests, or quotations;
- use placeholders only when the user asked for a template;
- make recommendations no stronger than the supplied evidence.

For a prompt or tool description, optimize for model interpretation and routing rather than literary
style. For a deck, keep one main claim per slide and separate on-slide copy from speaker notes.

### 5. Revise silently

Before returning:

1. verify that the draft performs the requested job;
2. compare every factual, causal, temporal, and evaluative claim with the supplied source, and remove
   anything merely plausible rather than supported;
3. move the answer, request, or decision earlier when that helps the reader;
4. remove repetition, filler, stock phrasing, and revision residue;
5. check paragraph focus, referents, and sentence structure;
6. read for the author's register rather than imposing a generic "professional" voice.

For reader-facing prose, finish with the concentrated
[`references/anti-slop.md`](references/anti-slop.md) pass. It checks recurring patterns through
relevance, evidence, clarity, and voice. Change a pattern only when it weakens this text; do not
replace a distinctive sentence merely because it resembles an example.

Fix issues you find. Do not return numeric scores, dimension names, a self-check transcript, or a
claim that the text is "fully optimized." Mention a deliberate tradeoff only when the user needs it
to evaluate the result.

### 6. Deliver

If you edited a file, make the smallest coherent edit and report:

- the file changed;
- the substantive changes;
- any unresolved content question or verification gap.

Otherwise return the finished text. Use a code block only when exact copying matters, such as a
prompt, configuration value, or tool description.

After an explicit de-slop edit, briefly name the main changes so the author can judge them.

Keep commentary after the draft brief. Do not bury the result under an explanation of the writing
process.
