---
name: felicity-review
description: >-
  Reviews writing for consequential problems in meaning, reasoning, structure, audience fit, and
  natural voice. Use when the user asks to review, critique, audit, proofread, assess, or find
  problems in an email, post, report, deck, README, prompt, system prompt, tool description, or model
  response. Reports prioritized findings with locations and concrete fixes, and can inspect text,
  DOCX, PPTX, RTF, DOC, and text-layer PDFs. Do not use when the user wants a new draft, a rewrite,
  or changes applied to a file; use felicity-write for that.
---

# Felicity Review

Find problems that would change a reader's understanding, action, trust, or effort. Report the
problems; do not edit the source.

## Workflow

### 1. Establish the target

Use the text, selection, file, or files named by the user. If none is present, ask for it.

Infer the intended reader and purpose from the request and the text. State a material assumption in
the verdict when needed. Ask a question only when different answers would change the review
substantially, such as whether a document is an internal working note or customer-facing copy.

Do not ask the user to classify the text or choose a rubric.

### 2. Read the text

Read plain-text and source files directly. For `.docx`, `.pptx`, `.rtf`, `.doc`, or `.pdf`, run:

```bash
python3 scripts/extract_text.py <path>
```

Resolve the script from this skill's directory. The script reads archives in place and writes
extracted text to stdout; it does not modify the source. PDF extraction requires `pdftotext`.

If extraction fails or returns no useful text, name the file and failed step, then ask for a text or
PDF export. Never review a document you did not read.

Extraction does not reveal meaning carried only by images, charts, or layout. Inspect a rendering
when those elements matter and the host can show one; otherwise state the text-only review scope.

For a deck, review on-slide copy and speaker notes as separate layers. Use slide numbers from the
extractor output.

### 3. Load the standard

Read [`references/review-standard.md`](references/review-standard.md) before reviewing. It defines
the issue threshold, review lenses, severity, and text-specific checks.

Do not reconstruct the old numeric rubric from memory. Numeric scoring is optional and only applies
when the user explicitly requests it.

### 4. Review by consequence

First identify the text's speech act: what it says, what it asks or commits the writer to, and what
the intended reader is likely to infer. Check the reader's shared context, the scope of claims and
qualifiers, and whether each sentence supplies relevant information at the point it is needed.
Use these linguistic and pragmatic questions to locate problems; keep the finding threshold in the
standard unchanged. Then check:

1. claims and reasoning;
2. purpose, answer, and force;
3. audience and context;
4. organization and paragraph coherence;
5. sentence clarity and economy;
6. voice, tone, and formulaic language;
7. instruction or routing quality when the reader is a model.

Stay within the requested scope. Before filing a missing-information finding, ask whether the absent
detail prevents this reader from taking the text's stated action or creates a likely false belief.
Do not expand a concise update into a demand for every operational detail that might be useful.

Treat facts carefully:

- Check whether conclusions follow from evidence stated in the text.
- Do not claim a factual statement is false unless the user supplied contrary evidence or you
  verified it.
- Label facts that need external verification as verification gaps, not errors.

File one finding per underlying problem. Do not multiply a single awkward sentence across several
lenses.

### 5. Report

Use this shape:

```markdown
<One-sentence verdict with finding count and the most important consequence.>

**Findings**
- **Major: <short title>** — `file:line` or `slide N`
  <What is wrong, why it matters, and the concrete fix.>
- **Moderate: <short title>** — `<location>`
  <What is wrong, why it matters, and the concrete fix.>

**Assumptions**
<Only assumptions that could change the result. Omit when none.>
```

Order findings by severity, then by reading order. Quote the smallest useful span. For a pasted
snippet without line numbers, use a short quote as the location.

Apply these reporting rules:

- Lead with findings, not a rubric tour.
- Keep each finding actionable.
- Group repeated surface tics into one finding with a count.
- Omit preference-level polish unless the user asked for line editing.
- If there are no findings, say so plainly and name any verification limit.
- Do not add a sales pitch for `felicity-write`.
- Never edit the reviewed source.
