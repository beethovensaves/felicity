# Felicity behavior evals

The cases in `cases.json` test the two skills' decisions and routing. They include unsupported
claims, shared context, request force, ordinary review restraint, voice preservation, technical
word senses, and formulaic writing. Review cases must keep Felicity's normal consequential finding
threshold. Most cases invoke a skill explicitly; routing cases omit the skill name.

For a larger external comparison, see the [paired EditEval and PUB sample](public-benchmarks/2026-09-29-codex/REPORT.md)
and its [runner](../scripts/run_public_benchmarks.py). It includes 170 source items, paired no-skill
answers, exact prompts, and task scores. It tests different behavior from these Felicity-specific
cases and does not replace review-restraint or voice-preservation checks.

See [selected observed runs](RESULTS.md) for complete final answers and manual grades from a small
Codex sample. The case catalog is larger than the published sample.

List or select cases without making a model call:

```bash
python3 scripts/run_evals.py --list
python3 scripts/run_evals.py --host codex --case review-causal-leap
```

Run an isolated case with the current skills:

```bash
python3 scripts/run_evals.py --host codex --case review-causal-leap --run
python3 scripts/run_evals.py --host claude --case write-technical-sense --run
```

The runner copies the two skill folders into a temporary project, uses read-only model tools, and
saves the final answer, process output, and case criteria under `evals/results/`. It never installs
the skills globally. Model runs may use account credits. Use `--skills-root /path/to/older/felicity`
to compare versions on the same cases.

For each result, inspect the final answer and enter `1` or `0` for each item in the result JSON's
`grades` list. Then summarize the case and overall scores:

```bash
python3 scripts/summarize_evals.py evals/results/<host>/<timestamp> --require-complete
```

Record any consequential failure alongside the score. The runner also reports missing protected
literals; this is a diagnostic signal, not a semantic score. Compare case-level results across
versions before changing a rule in response to one example. Add both a positive case and a
plausible false-positive case for a new pattern.
