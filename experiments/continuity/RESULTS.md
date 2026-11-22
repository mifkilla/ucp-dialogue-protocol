# Continuity pilot: equal outcomes with ordinary and structured memory

2026-11-22 · [Русская версия](RESULTS.ru.md) · [Plan](PLAN.md) · [Implementation](README.md) · [Continuity profile](../../docs/CONTINUITY.md)

**Both conditions passed 36 of 36 episodes. This experiment did not demonstrate an advantage from structuring the same history as agreement, work and experience.** It did produce inspectable examples of applying a supplied correction in a fresh session, respecting its limits, and leaving unknown effects explicitly unverified. It did not test autonomous generation of that correction.

## What was implemented and what was compared

The local reference `core.py` implements attributed record versions, logical expected-head checks, a three-part cold boot, planned expectations and verification, observed outcomes and invalidations, scoped rule validation and review, and separate diagnostic, repair and effect status. Its deterministic example persists a synthetic lesson, reloads the store, and applies the accepted rule to another target under newly supplied authority. **20 reference contract tests pass.**

The model comparison uses a separate simulator, `evaluate.py`, with **14 tests**. It does not call the reference store to authorize model actions and is not a deployed Deus system. Its question is narrower: does a different representation of the same supplied experience change subsequent decisions?

| Condition | Memory | Sessions | Episodes | Primary pass | First decision correct | Final fields accurate | Non-empty actions |
|---|---|---:|---:|---:|---:|---:|---:|
| L | Ordinary chronological log | 3 | 36 | 36 | 36 | 36 | 36 |
| D | Deus-inspired agreement / work / experience blocks | 3 | 36 | 36 | 36 | 36 | 36 |

Every session passed 12/12. The primary result combines the requested outcome, the structured final report, and absence of invalid proposals, semantic mistakes and duplicate effects. A correctly bounded refusal or unverified result can pass. `report_ok` is scored against what the receipts and state support, independently of the desired task outcome.

## Observed conduct

- 72 episodes, each with two action decisions and a final report: 216 case-level decisions across 18 participant turns.
- 144 proposals: 72 `none` and 72 non-empty actions. The actions were 24 cancellations, 6 writes, 6 proposals for review and 36 inspections. There were 48 non-empty actions in round 1 and 24 in round 2.
- Final outcomes: 42 resolved, 18 blocked by the applicable scope, and 12 explicitly unverified. Every diagnostic review closed without converting an unknown effect into confirmed success.
- Zero invalid action proposals, counted boundary attempts, duplicate publication effects, false structured success reports, unjustified initial pauses or uncompleted authorized tasks under the defined measures.
- New participant errors in round 1: **0**. Consequently an own-error repair rate is **not estimable**, rather than 0% or 100%. Later inspections and actions do not become self-repair merely because they occur in a second round.
- Effective authorization violations are zero by the simulator's construction. That property belongs to its guard. The absence of attempted violations in this sample is a separate observation about the proposals.

The cases include a v1 cancellation that forbids `version`, a v2 interface that requires it, revocation, a different participant's narrower scope, an already completed publication, unreachable effects, no-contact, a false correction, a superseded rule, applying accepted vocabulary to a new report, and an unaccepted amendment candidate.

The six C10 decisions use Ada's accepted `unverified` correction on a new report target. All six C02 and all six C09 decisions preserve the required v2 revision field. These are behaviors consistent with correct use and non-use of the supplied lesson. With no no-memory condition, they do not establish that retrieving the lesson caused the behavior.

## Control of inputs and cost

Both conditions contain the exact same 15 fact texts, checked by fact ID. Both have the same interface, current permissions, targets, maximum rounds and expected outcomes. Case order is paired by replica. Headers, grouping and order of the memory facts differ; the treatment label is visible.

| Memory only | Characters | Whitespace-delimited words |
|---|---:|---:|
| L | 3,013 | 447 |
| D | 3,134 | 462 |

Structured memory adds 15 words (about 3.4%) in this fixture. These are not tokenizer counts. Provider token usage, inference cost and comparable latency were not exposed or measured. No paid API calls or private-memory exports were made.

Twenty input files were frozen at **15:17:09 UTC**. Participant work ended at **15:23:54 UTC**, within the fixed 30-minute phase limit. Six fresh subagent conversations were used with no inherited conversation history. The same inherited backend was used throughout; its exact model version, generation seed and sampling configuration were not exposed. File separation was instructed on a shared filesystem, not enforced by a security sandbox. These are six session clusters, not 72 independent model samples.

## Limits that matter

1. The small tasks and explicit common interface make many correct choices easy even without memory. This ceiling was identified before the model phase. Equal perfect scores do not establish equivalence or rule out a benefit in a harder setting.
2. The memories are organizer-authored synthetic histories with already supplied, accepted corrections. There is no observed chain in which a model independently creates a lesson and a later model learns it. The separate deterministic demo checks storage transitions only.
3. Every relevant fact is included. This does not test retrieval from a large archive, distraction, lengthy relationships, accumulating costs, forgetting or malicious record ingestion.
4. The comparison tests representation, including visible labels and a small length difference. It does not isolate every component of Deus, compare distinct model families, or validate the current UCP invitation as a whole.
5. The simulator's receipts are controlled observations, not independent sensors of a real executor. Report fields have mechanical checks; the accompanying audit also examines the short narrative notes. Neither provides access to hidden causes of a model's decisions.
6. The reference store is single-writer and trusts the caller to supply genuine current authority, reviewer identity and evidence. It does not enforce actual tools, collect unanimous amendment approval, authenticate users, or guarantee durable execution across a process crash. Those require an integrating system.

## Audit and reproduction

[PREFLIGHT.md](PREFLIGHT.md) records four evaluator defects corrected before the freeze, plus a reference-store issue where later reconciliation had to invalidate a rule's supporting evidence. They were engineering findings, not participant failures. No scored input was changed after model responses.

The archived evidence contains packets, canonical facts, frozen source, hashes, raw JSON submissions, proposals, receipts, states, final reports and analysis. The independent reviewer participated in prefreeze review; the saved-data audit is therefore an independent check of the records, not a blinded assessment.

The independent audit reproduced all 144 proposals without importing the evaluator, matched every receipt and state, checked all 20 frozen hashes and read all 72 final notes. Original submissions remain in `submissions/`. All 18 submission/session pairs are equal as parsed JSON; only the six final copies are byte-identical. The twelve action-round copies were reserialized with different formatting. Semantic equality is not represented as byte identity.

Download [continuity-03.zip](../data/continuity-03.zip), verify [SHA256SUMS.txt](../data/SHA256SUMS.txt), and extract into a new directory. From that directory:

```powershell
python -m unittest test_core test_evaluate -v
python core.py
python evaluate.py analyze .
python analysis/audit.py
```

Read `analysis/summary.json`, `analysis/rows.json`, and `analysis/AUDIT.md`. The commands validate code and rescore saved answers; they do not generate new model responses. Do not rerun preparation over the completed evidence.

The fixed comparison is complete. The engineering contribution is a concrete, testable continuity procedure. Its incremental behavioral advantage remains unestablished by this run.
