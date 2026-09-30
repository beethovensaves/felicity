# Public benchmark sample: Codex, September 2026

This is an exploratory, paired run on **170 official benchmark items**: 30 sentence edits from
EditEval's IteraTeR test split and 140 multiple-choice questions from all 14 PUB tasks. It is a
fixed sample, not a run of either full benchmark or an official leaderboard submission. The
[manifest](manifest.json), [scores](scores.json), and each condition's exact prompts and answers
are included here. The [runner](../../../scripts/run_public_benchmarks.py) reproduces selection,
execution, and scoring.

## Results

| EditEval task | Items | No skill SARI | Felicity SARI | Difference |
| --- | ---: | ---: | ---: | ---: |
| Clarity | 10 | 21.12 | 24.95 | +3.83 |
| Coherence | 10 | 36.20 | 36.92 | +0.71 |
| Fluency | 10 | 47.57 | 43.86 | −3.70 |
| **All sampled edits** | **30** | **33.50** | **34.63** | **+1.13** |

The unchanged inputs score 31.39 SARI. A paired bootstrap that resamples within each task
(2,000 replicates, seed 793) gives a 95% percentile interval of **−0.58 to +2.86 SARI** for
Felicity's difference from the no-skill condition. This sample does not establish a reliable gain.
Scores use [EditEval's SARI implementation](https://github.com/facebookresearch/EditEval/blob/main/src/metrics/easse_sari.py)
with one human reference per item.

| PUB task | No skill | Felicity |
| --- | ---: | ---: |
| 1 Direct/indirect answer | 6/10 | 6/10 |
| 2 Response without implied meaning | 10/10 | 10/10 |
| 3 Response with implied meaning | 10/10 | 10/10 |
| 4 Implicature recovery | 8/10 | 8/10 |
| 5 Agreement detection | 10/10 | 10/10 |
| 6 Sarcasm | 10/10 | 10/10 |
| 7 Figurative language, no hint | 10/10 | 10/10 |
| 8 Figurative language, positive hint | 10/10 | 10/10 |
| 9 Figurative language, contrastive hint | 10/10 | 10/10 |
| 10 Implicature NLI | 6/10 | 6/10 |
| 11 Presupposition NLI | 9/10 | 10/10 |
| 12 Presupposition over QA | 7/10 | 7/10 |
| 13 Deictic QA | 10/10 | 10/10 |
| 14 Reference via metonymy | 9/10 | 9/10 |
| **All sampled questions** | **125/140** | **126/140** |

The two conditions gave the same answer on **139 of 140 PUB questions**. The only difference was
task 11, source ID 1668: from “If Amanda had left, it's okay,” the question asks whether “Amanda
wasn't here” is definitely true, possibly true, or definitely false. PUB marks *definitely false*;
Felicity chose that label and the no-skill run chose *possibly true*. The premise does not establish
that Amanda was or was not here, so this scored gain is not convincing evidence of better pragmatic
reasoning.

The sample contains other questionable PUB labels. In task 10, source ID 1081, “Neither these
mushrooms nor these restaurants have stunned Tina” is paired with “These mushrooms and these
restaurants haven't both stunned Tina.” PUB labels the hypothesis *definitely false*, although it
follows from the premise. These labels are retained in the raw score to avoid changing the test
after seeing the answers; they limit what that score means.

EditEval's single references also reward choices that can conflict with Felicity's purpose. One
fluency reference changes “Paderap has four sons” to “Paderap had four sons,” changing the temporal
claim. A coherence reference removes the ocean's participation in the carbon and water cycles.
Felicity preserved those claims. SARI measures overlap with the reference edits, so it cannot by
itself establish whether the resulting prose preserved meaning or the writer's voice.

## Method and limits

- **Sources.** [EditEval](https://github.com/facebookresearch/EditEval) uses the
  [IteraTeR human sentence test split](https://huggingface.co/datasets/wanyu/IteraTeR_human_sent)
  for fluency, clarity, and coherence. The PUB questions come from the
  [authors' dataset](https://huggingface.co/datasets/cfilt/PUB). Source archive hashes are in the
  manifest. Source revisions were EditEval `013cd20`, IteraTeR `e22e037`, and PUB `65a6a87`.
  The sampled texts are attributed to their source datasets, whose published licenses are
  [Apache 2.0 for IteraTeR](https://huggingface.co/datasets/wanyu/IteraTeR_human_sent) and
  [MIT for PUB](https://huggingface.co/datasets/cfilt/PUB).
- **Sampling.** Python's `random.Random(20260929)` selected 10 distinct source texts from each
  EditEval category and 10 valid-option questions from each PUB task. Selection happened before
  full-run scoring. Clarity and PUB task 10 were used to check the execution protocol.
- **Model.** Codex CLI 0.158.0 ran `gpt-6-astra` with medium reasoning. Each task's 10 items were
  answered in one structured-output call per condition. The same items, model, and task instructions
  were used in both conditions. The Felicity prompt explicitly directed Codex to read the relevant
  project skill and references; the no-skill prompt omitted that direction. Global Felicity
  installations were disabled for both conditions. All 17 Felicity calls read a skill; none of the
  17 no-skill calls did.
- **Scope.** This run tests `felicity-write` on sentence edits and the linguistic guidance in
  `felicity-review` on PUB questions. PUB is a question-answering test; Felicity's review skill is
  intended for consequential writing review. Neither benchmark tests review restraint, authorial
  voice, or removal of formulaic prose directly. Ten items per task, one model, one run per condition,
  and batch prompting make these results diagnostic rather than a population estimate or a
  leaderboard-comparable score. Claude Code was not run because its local OAuth session had expired.

## Reproduce

Download the [IteraTeR test JSON](https://huggingface.co/datasets/wanyu/IteraTeR_human_sent/resolve/main/test.json)
and PUB's `task_1.zip` through `task_14.zip` from the [authors' data directory](https://huggingface.co/datasets/cfilt/PUB/tree/main/data).
Clone EditEval for its SARI implementation. Then run from this repository:

```bash
python3 -m venv /tmp/felicity-bench-venv
/tmp/felicity-bench-venv/bin/pip install nltk sacrebleu sacremoses
/tmp/felicity-bench-venv/bin/python scripts/run_public_benchmarks.py prepare \
  --iterater-test /path/to/test.json --pub-dir /path/to/pub-zips \
  --out /tmp/felicity-manifest.json --count 10
/tmp/felicity-bench-venv/bin/python scripts/run_public_benchmarks.py run \
  --manifest /tmp/felicity-manifest.json --out /tmp/felicity-results --workers 2
PYTHONPATH=/path/to/EditEval /tmp/felicity-bench-venv/bin/python \
  scripts/run_public_benchmarks.py score --out /tmp/felicity-results --bootstrap 2000
```

The `run` step makes 34 Codex model calls. It saves the prompts, structured answers, model settings,
skill-read checks, and task scores. Runs may vary across time even with a pinned model name.
