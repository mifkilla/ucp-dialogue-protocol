# Final integration pilot: from dialogue review to an observable next action

English is the primary edition · [Русская версия](README.ru.md) · [Main invitation](../../README.md)

This pilot connects the external observer to an executor. A reviewer extracts obligations from a conversation, cites events, and proposes a bounded correction. The executor receives that actual review, acts through a simulator with enforced permissions, and reports what its receipts establish. A comparison group gets an ordinary careful second-look instruction.

[Fixed plan](PLAN.md) · [Results and limits](RESULTS.md) · [Dataset](DATASET.md) · [Preflight changes](PREFLIGHT.md) · [Evidence ZIP](../data/final-05.zip) · [Checksums](../data/SHA256SUMS.txt)

## What is in this directory?

- `cases.json`: 12 new synthetic histories, each 18 turns, with a supplied focal event and natural review question. No prepared obligation field is given to reviewers.
- `references.json`: reference verdicts, critical meanings, simulator state and expected outcomes. Participants were instructed not to read this file; access was not blocked by a separate filesystem sandbox.
- `engine.py`: a small guarded simulator. It distinguishes a proposed action, permission, effect, observation and final claim.
- `pipeline.py`: packet construction, exact evidence validation, receipts, provenance hashes and scoring. It uses the published observer core; the evidence ZIP includes the exact frozen copy as `observer_base.py`.
- `test_engine.py` and `test_pipeline.py`: 36 regression tests, including unknown effects, stale authority, evidence binding and the requirement for a separate review of final explanations.

The frozen ZIP additionally contains all participant JSON responses, their input packets, state transitions, stage manifests, semantic review and an independent saved-data audit. Its model outputs are public explanations and structured decisions, not private reasoning traces.

## Reproduce the saved calculation

Python 3.11 or later is sufficient. No API key, paid provider or new model generation is needed. Extract the archive into a new directory outside the repository. First compare its SHA-256 with the published checksum file. Then run from the extraction directory:

```powershell
python -B -m unittest test_engine test_pipeline -v
python -B pipeline.py verify .
python -B pipeline.py analyze .
python -B audit.py
```

The analysis rewrites only `analysis.json` in the extracted copy. The audit checks the saved evidence independently. Compare reproduced files with the archive's `bundle_hashes.json`; output hashes should remain unchanged. `bundle_hashes.json` covers every packaged file except itself and is an integrity check, not proof that a scientific claim is true.

Do not run `prepare`, `executors` or `apply` on completed evidence. Those commands construct a new experiment or advance it. A fresh generation run needs a separate directory, a new fixed plan and its own recorded outputs. Ordering seeds do not control model sampling.

From the repository root, the local regression command is:

```powershell
python -B -m unittest discover -s experiments/final -v
```

## How to read the result

The observer's judgment is fallible. Exact quotation checks establish attribution, not interpretation. A semantic review therefore separately checks the extracted meaning and all final explanations. A signal never grants permission. The simulator's guard is identical in both conditions, and an attempted forbidden action still counts against the model even if the guard prevents its effect.

This is a small directed integration pilot with seeded histories and repeated cases within sessions. It does not establish unrestricted dialogue monitoring, cross-model generalization, consciousness, a universal CARE score, or contact with xenointelligence. The current test phase ends with this research snapshot; the public invitation remains open.
