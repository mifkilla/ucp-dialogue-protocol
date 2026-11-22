# UCP continuity: reference code and a bounded memory-transfer experiment

[Русская версия](README.ru.md) · [Optional continuity profile](../../docs/CONTINUITY.md) · [Plan](PLAN.md) · [Results](RESULTS.md)

This directory contains two distinct artifacts:

- `core.py` is a small local reference store for attributed corrections, current-agreement cold boot, planned actions, outcomes and scoped rule review. It uses only Python 3.11+ standard-library modules. It performs no external actions.
- `evaluate.py` is a separate synthetic simulator comparing ordinary chronological history with the same facts grouped into agreement, work and experience. Its model experiment tests that representation change, not the entire reference store or a production Deus deployment.

From this directory:

```powershell
python -m unittest test_core test_evaluate -v
python core.py
```

The second command runs a deterministic example across a persisted reload. It is not a new model run. The reference tests check successful and rejected transitions, including stale records, revoked permission, unknown effects, scope changes, rule validation and independent closure.

The store is single-writer JSONL. Expected-head checks are logical checks within one instance, not cross-process locking. Identity, current permission, reviewer authority and external evidence must be authenticated and supplied by the integrating application. Permission must be checked again at actual execution. The store is not an instrument interceptor. Its hash chain detects inconsistent edits, not fabricated evidence or a complete consistent rewrite. Effect targets must identify a particular operation, so that repeat protection does not accidentally prohibit unrelated future work.

Do not connect this example to private records or live infrastructure without an appropriate design and authorization. Its public examples use synthetic participants and resources. It requires no provider key and imports no personal memory.

## Reproducing saved results

The [completed report](RESULTS.md) and [archived evidence](../data/continuity-03.zip) identify the exact frozen inputs, six sessions, 72 episodes and hashes. Both conditions passed 36/36; no advantage was demonstrated. Rescoring existing answers does not generate new answers or establish behavior on new tasks. A new experiment must use a new directory; `prepare` refuses to overwrite one.

The fixed comparison is defined in [PLAN.md](PLAN.md). Its source history is organizer-authored and includes supplied corrections. Therefore success cannot be described as independently discovering an error, generating a lesson and learning autonomously across sessions.
