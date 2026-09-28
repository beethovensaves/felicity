# Observed behavior

These are selected live Codex runs from 2026-09-28 using the skills in this repository. Codex CLI
version: `0.157.0`. Each case ran in a temporary project with the skill invoked explicitly. The
linked files contain the complete final answers; the case prompts and grading criteria are in
[`cases.json`](cases.json). The scores below were judged manually against those criteria, one point
per criterion. They are a small sample, not a general performance estimate.

| Case | Result | What the answer did |
| --- | ---: | --- |
| [`review-causal-leap`](observed/codex/review-causal-leap.txt) | 3/3 | Identified the unsupported move from timing to removing Redis and recommended isolating the cause. |
| [`review-staging-scope`](observed/codex/review-staging-scope.txt) | 3/3 | Reported no finding for a concise update that clearly limited completion to staging. |
| [`write-empty-praise`](observed/codex/write-empty-praise.txt) | 3/3 | Asked for a concrete product fact instead of replacing vague praise with synonyms or inventing a benefit. |

The first run of `write-empty-praise` produced another generic sentence. We added a targeted
instruction against synonymous praise and reran the case; the linked answer and score are from the
rerun. This report does not claim that all 14 cases, implicit routing, or Claude Code behavior passed.

To reproduce a case from a source checkout, run:

```bash
python3 scripts/run_evals.py --host codex --case review-causal-leap --run
```

The runner writes ungraded records under `evals/results/`. Read the final answer, enter `1` or `0`
for each criterion in its JSON record, then use `scripts/summarize_evals.py` for a summary. Results
can vary across model versions and runs.
