# Observer stress pilot: longer histories and review of actual proposals

English is primary · [Русская версия](README.ru.md) · [Main invitation](../../README.md)

This follow-up asks where review might help after the earlier pilot reached a ceiling. It uses original synthetic tasks inspired by published work on untrusted tool outputs, updated memory, error localization and tool-assisted correction. It is not a run of those original benchmarks. [Sources and differences](SOURCES.md).

[Prospective plan](PLAN.md) · [Results](RESULTS.md) · [Dataset and contract](DATASET.md) · [Preflight](PREFLIGHT.md) · [Evidence archive](../data/stress-06.zip) · [Checksums](../data/SHA256SUMS.txt)

## The comparison

Two initial sessions propose plans for the same 12 cases. Each case has 80 attributed events, 12 candidate actions and explicit hard limits. An observer reviews each actual initial proposal. The exact same proposal is then reconsidered in three conditions:

| Condition | Additional input |
|---|---|
| S | An ordinary substantive second-look checklist |
| O | The actual fallible observer review, with event references |
| K | The same observer review plus deterministic diagnostics of the original proposal |

The checker reconstructs current permission, spending and unresolved effects from the same public facts. It provides totals and violated constraints, not an optimal solution. A separate exhaustive optimizer is used only for scoring. All equally optimal admissible plans are accepted. Participants read and reason without executing a code solver; K's computed input is an explicit advantage under study. No claim is made about outperforming an unrestricted coding agent.

Initial plans are not executed. A revised plan executes once through an identical atomic guard, then its author receives the actual receipt and submits a structured report. The comparison is designed to assess correction of actual model proposals before execution. This run contained no initial errors, so repair was not estimable. It does not measure autonomous recovery from an already executed harmful action.

A separate block supplies four fixed incorrect reviews to each repeat. These contain real quotations but draw a false permission conclusion. They are organizer-authored negative controls, not mistakes attributed to the real observer.

## What can be calculated?

Permission, resource totals, duplicate effects, dependency satisfaction and report agreement have explicit toy-system rules. These can be checked by code. The agreed task-value objective is also numerical. It is not a measure of care or love. A permitted but suboptimal plan loses task value without thereby becoming a UCP violation.

The event envelopes are assumed authoritative within the simulator. The code does not authenticate a real owner, infer genuine consent, or make an external tool stop. Exact quotation checks establish attribution; a model's interpretation can still be wrong.

## Reproduce saved results

Use Python 3.11 or later. No API key, new model response or dependency installation is required. Verify the ZIP against `SHA256SUMS.txt`, extract it to a new directory outside this repository, and run there:

```powershell
python -B -m unittest test_engine test_pipeline
python -B reference_audit.py
python -B pipeline.py verify .
python -B pipeline.py analyze .
python -B audit.py
```

These commands rescore saved outputs. They do not regenerate stochastic model answers. Compare every file with `bundle_hashes.json`; deterministic output files should keep their original hashes. The bundle manifest covers every file except itself.

Do not run `generate_cases.py`, `prepare`, `observers`, `revisions` or `execute` on completed evidence. Those commands create or advance an experiment. New generation needs a new directory, prospective criteria and its own complete record.

Repository regressions run with:

```powershell
python -B -m unittest discover -s experiments/stress
```

Case IDs, order seeds, frozen hashes, raw proposals, actual reviews, computed diagnostics, receipts and reports are retained in the archive. Exact backend snapshot and sampling settings were not exposed by the runtime. File isolation was instructed on a shared filesystem. Results are descriptive and clustered by session; they do not establish general effectiveness or independent cross-model replication.
