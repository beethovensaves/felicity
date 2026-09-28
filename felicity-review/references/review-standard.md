# Felicity Review Standard

Use this standard to find consequential writing problems. It is a decision aid, not a checklist that
must produce findings.

## Linguistic and Pragmatic Basis

Read a text as an action in a particular conversation, not as sentences in isolation:

- **Speech act and force:** Identify the claim, question, request, recommendation, or commitment.
  Check whether the wording gives it the intended strength and whether the reader knows what to do.
- **Common ground:** Infer what this audience already knows. Supply missing context only when its
  absence would cause a real misread or block the intended action.
- **Scope and implication:** Check what qualifiers, negation, tense, and framing imply beyond the
  literal sentence. A true narrow statement can still invite an unsupported broad conclusion.
- **Information flow:** Put given context near the new point it supports. Keep referents stable and
  let sentences and paragraphs advance a recognizable topic.
- **Cooperation (quantity, quality, relation, manner):** Give enough information for the task,
  support load-bearing claims, stay relevant, and make the relationship between ideas clear.
  Repetition, inflated importance, and stock transitions matter when they make the reader work
  harder or trust the text less.

Use these as diagnostic questions, not labels to paste into findings. A finding still needs the
reader consequence and concrete fix required below.

These questions adapt [Grice's cooperative principle](https://web.stanford.edu/class/psych205/papers/Grice-1975.pdf)
and [Clark's account of common ground](https://web.stanford.edu/~clark/1990s/Using%20language/Clark.Ch4.Using%20Language.96.pdf)
to written communication. They do not turn either framework into a mechanical score.

## Finding Threshold

Report an issue only when you can name:

1. the intended reader or model;
2. the likely misread, wrong action, loss of trust, or avoidable effort; and
3. a change that improves the text without changing its intended meaning.

Do not report:

- harmless personal preference;
- a technical term used in its technical sense;
- a deliberate rhetorical choice that suits the reader;
- a fact merely because the text does not cite it, unless the claim is load-bearing and the genre
  calls for support;
- the same underlying problem under several headings.

Missing information is a finding only when the text's purpose requires it. Do not demand adjacent
details merely because they would be useful in a longer document. A concise status update does not
automatically need customer impact, rollback steps, recovery contingencies, every validation type,
or the definition of a threshold already shared by its internal audience.

Read scope literally. "Complete in staging" states a staging milestone, not production readiness. It
can coexist with a pending load test and an enabled fallback path. Flag the sentence only when the
text erases that scope or uses it to support a broader readiness claim.

Treat ordinary internal references such as "Tuesday," "the existing threshold," or a known project
name as shared context unless ambiguity creates a concrete action risk for the stated reader.

## Severity

Assign severity from the consequence, not from the category.

- **Major:** likely to cause a wrong decision, wrong model behavior, unsupported confidence, or
  failure of the text's primary purpose.
- **Moderate:** likely to cause a material misread, delay, unnecessary reader effort, or a noticeable
  loss of credibility.
- **Minor:** localized polish that matters to the requested standard but does not threaten the
  outcome. Include only for proofreading or line-editing requests.

When uncertain between two levels, use the lower one and explain the risk precisely.

## Review Lenses

### 1. Claims and reasoning

Check whether:

- the text distinguishes observed fact, inference, estimate, and recommendation;
- each load-bearing conclusion follows from the evidence the text states;
- qualifiers match the evidence;
- a causal claim has more support than timing or correlation;
- the text implies completeness despite an unperformed or unknown step;
- citations or provenance appear where this reader would use them.

Textual support and factual truth are different. You can review the first from the document. Verify
the second only when evidence or research tools are available.

Example:

> Latency rose after the cache change, so we should remove Redis.

The timing does not isolate Redis as the cause. Recommend further isolation or narrow the conclusion
to the observed latency change.

### 2. Purpose, answer, and force

Check whether:

- the main answer, decision, request, or recommendation appears early;
- the reader can tell what to do next;
- requirement, suggestion, estimate, and commitment are distinct;
- the text answers its stated question rather than a nearby one;
- headings state the useful point instead of naming a broad topic.

Do not force an answer-first structure onto genres that need chronology, suspense, or a conventional
opening.

### 3. Audience and context

Check whether:

- jargon and detail fit the actual reader;
- necessary context is present once, near its first use;
- tone matches the relationship and stakes;
- an external deliverable omits revision history and private process notes;
- a working document retains uncertainty and audit detail needed by collaborators.

The distinction is audience, not storage location. A public README is an external artifact even
though it lives in a repository.

### 4. Organization and coherence

Check whether:

- sections appear in the order the reader needs them;
- each paragraph has a controlling subject or purpose;
- consecutive sentences connect through a shared subject, referent, or logical step;
- one unit does not carry several unrelated claims;
- lists group comparable items and use parallel structure;
- decks carry one main claim per slide and keep notes separate from on-slide copy.

When a paragraph feels scattered, inspect its sentence subjects. Rewrite the openings only when that
reveals the problem; do not enforce repeated wording mechanically.

### 5. Sentence clarity and economy

Check whether:

- actors and actions are easy to identify;
- pronouns and modifiers have one likely referent;
- verbs carry the action instead of padded noun phrases;
- clauses are ordered for an easy first reading;
- every phrase contributes meaning;
- punctuation clarifies the relationship between ideas.

Passive voice, nominalization, sentence length, and em dashes are signals, not faults by themselves.

### 6. Voice and formulaic language

Check whether the text sounds specific to its author, audience, and subject. Flag patterns such as:

- praise without evidence: "powerful," "world-class," "game-changing";
- ceremonial openings: "In today's fast-paced world," "Great question";
- stock contrasts: "not just X, but Y";
- abstract AI-favored verbs where a plain verb is more exact: "delve," "leverage," "unlock";
- repeated transition words, dramatic punctuation, padded triads, or section-marker emoji;
- self-certification: "every claim is verified";
- revision residue that an external reader cannot use.

Context controls. "Robust to packet loss," "financial leverage," and a deliberate em dash may be
the clearest choices. Treat any broader word list as candidate generation, never as automatic
evidence of a defect.

### 7. Model-facing instructions and routing

For prompts and system prompts, check whether:

- the task, constraints, and output format are explicit;
- terms and priorities are unambiguous;
- positive target behavior accompanies prohibitions;
- conflicting rules have a stated priority;
- examples clarify rather than accidentally narrow the task.

For tool and skill descriptions, check whether:

- the opening states the capability and user situation;
- likely trigger words appear naturally;
- the boundary against sibling tools is clear;
- the description matches actual behavior;
- matching surface is not diluted by implementation detail or praise.

## Optional Numeric Scores

Score only when the user asks. Apply one score to each requested lens:

- **5:** no material issue;
- **4:** minor issue only;
- **3:** moderate issue;
- **2:** major issue;
- **1:** the text cannot achieve its purpose as written.

Explain scores through findings. Do not treat the number as more precise than the judgment behind it.
