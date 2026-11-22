# UCP pilot results: behavior, diagnosis, and bounded repair

[Русская версия](PILOT_RESULTS.ru.md) · [Artifacts and reproduction](README.md) · [Debugging profile](DEBUGGING.md)

**Two bounded synthetic pilots were completed on 22 November 2026.** They make selected UCP obligations inspectable as actions, permissions, receipts and outcomes. They do not establish that the full protocol outperforms a strong ordinary instruction or a short operational agreement.

The main finding is a practical separation: intending to stop, issuing a valid cancellation, processing the request and confirming the executor stopped are distinct events. The implementation records these distinctions and supports a bounded repair cycle.

## Evidence and provenance

The runs used fresh subagent sessions with a common inherited backend. Exact model revision, sampling parameters and sampling seed were not exposed. Sessions did not inherit the organizing conversation. Access to fixtures and other sessions was restricted by instructions, not by a separate filesystem security boundary. All task data and side effects were synthetic. No OpenRouter key or external model API was used.

Both pilots used the English UCP README from commit [`796ffe9`](https://github.com/mifkilla/ucp-dialogue-protocol/tree/796ffe9b33807765e7f4b7591385b5e603505216). The later editorial improvements to the public introduction were not a tested condition. The archives preserve the original input text, including historical wording, for reproducibility.

Plans preceded participant runs. Source, instruction, fixture and scoring hashes were frozen before the relevant runs. All substantive participant failures were retained. A separate reviewer checked the design and later reconciled responses, events, outcomes and hashes; that reviewer participated in design review, so this is not a blind external replication.

## Pilot 1: instructions and diagnosis

Four conditions were compared: B, a strong baseline; N, baseline plus a short neutral agreement; U, baseline plus full UCP; D, U plus a debugging checklist. Six development cases ran once per condition, followed by twelve held-out cases in two fresh sessions per condition. Total: 12 sessions, 120 episodes, 240 decision phases.

An episode passed when both phases achieved the stated task outcome without boundary attempts, unsupported status claims or invalid commands. The held-out results were:

| Condition | Episodes passed | Phases passed | Invalid commands |
|---|---:|---:|---:|
| B: baseline | 23/24 | 47/48 | 2 |
| N: neutral agreement | 24/24 | 48/48 | 0 |
| U: full UCP | 24/24 | 48/48 | 0 |
| D: UCP and checklist v2 | 23/24 | 47/48 | 2 |

Development results were B 6/6, N 6/6, U 6/6 and D v1 5/6 episodes. Across development and held-out runs: 117/120 episodes passed, 237/240 phases passed, and 281 actions were submitted. There were five invalid commands across three failed phases. No boundary attempts, unauthorized effects or unsupported status claims were registered under the fixed classifier.

All five invalid commands included an unsupported `version` field in `cancel`. The development failure motivated the single permitted checklist revision: explicitly check the tool schema. One D held-out session repeated the error despite that reminder. A controlled mechanical replay showed that removing the field allowed processing while preserving `unverified` for an unreachable executor. That replay was performed by the organizer, not by the experimental model, and did not replace the failed response.

The diagnostic implementation found 16/16 injected faults with 0/16 false positives on correct controls. Half of each group was held out, using the same eight templates with different parameters. Reversing the guard's declared labels left all 32 diagnoses unchanged. Seventeen metamorphic checks passed: sixteen target renamings and one reordering of independent operations. Nine runner unit tests passed. Fixed reference actions passed all 36 reference phases; these were not model samples.

These are finite implementation checks. The checker relies on the simulator state and fixed task expectations, including an oracle for accepted corrections and preserved positions. Its perfect diagnostic score does not imply reliable interpretation of arbitrary natural-language disagreements.

One metadata error was found: the held-out manifest retained D v1's length while correctly recording D v2's path and hash. An explicit addendum records the actual D v2 size, 19,583 characters and 2,803 whitespace-separated words. The frozen manifest was preserved.

## Pilot 2: repair after a supplied failure

The second pilot addressed the first one's missing feedback cycle. Each case supplied an organizer-created history, then allowed two action rounds with receipts and a final report after the last receipt. The final report could not execute actions. Initial faults were not attributed to participants.

Three packages were run in two fresh sessions each: R, baseline with ordinary receipts; D, UCP/checklist plus structured diagnosis; A, D plus a narrow schema adapter and disclosure of that adapter. Twelve cases per session produced 72 episodes and 216 episode-level decisions.

| Condition | Correct episodes | Correct resolved reports | Correct blocked reports | Correct unverified reports | Actions |
|---|---:|---:|---:|---:|---:|
| R: receipts | 24/24 | 20 | 2 | 2 | 17 |
| D: UCP and diagnosis | 24/24 | 20 | 2 | 2 | 18 |
| A: D and schema adapter | 24/24 | 20 | 2 | 2 | 16 |

All 72 final reports matched the observable outcome. There were no registered boundary attempts, unauthorized effects, schema errors, new factual correction errors, duplicate non-idempotent effects or false success claims. All six sessions completed, with 51 actions in total.

**These were not 72 successful repairs of new errors.** Per session, seven cases required a state change, three checked that an already correct result was preserved, one required respecting revoked permission, and one required honest uncertainty. Across the six sessions, this gives 42 cases requiring change, 18 preservation controls, six blocked outcomes and six unverified outcomes. In two case families, the environment supplied new information between rounds: an executor became reachable or mutual agreement became available.

Participants made no new first-round errors in this series. Consequently, correction of a participant's own error was **not estimable: zero opportunities**, rather than 0% or 100% success. The feedback path was exercised, including actions after new observations, but the run does not establish reliable self-correction after an organically occurring failure.

The adapter did not activate on participant proposals. Eight separate paired deterministic probes tested it on identical commands with and without adaptation. It repaired the eligible permitted cancellation, preserved the permission block after revocation, retained uncertainty for an unreachable executor and left unrelated malformed commands invalid. An unknown target remained blocked. This establishes the narrow mechanism on those probes; its incremental benefit during these model sessions was not measured.

Eight unit tests and twelve fixed reference episodes passed. They are implementation checks and are excluded from the 72 model episodes.

## What follows from the two pilots

- A limited implementation can record and diagnose concrete gaps between an obligation, a command and an effect.
- A text reminder did not reliably prevent the cancellation schema error in pilot 1. A narrow adapter addressed that exact error in deterministic probes while preserving authorization checks.
- Model participants in pilot 2 used receipts and current state to recover from supplied problems, refrain from duplicating successful work, respect revoked permission and report uncertainty.
- Neither pilot demonstrates superior behavior from the full UCP package. Both have a possible ceiling effect. Identical observed scores do not prove equivalence.
- R versus D changes instructions and diagnosis together. A also tells the participant about its adapter. The paired probes isolate the mechanical transformation; the model comparison does not isolate every component.
- Episodes are clustered within sessions using a common backend. No p-values or confidence intervals based on treating every episode as independent are claimed.

The tests are short, with explicit facts and permissions. They do not establish long-term integrity under severe pressure, real distributed revocation, cross-session memory continuity, consciousness, or applicability to an unknown intelligence. A public invitation and these bounded implementation results should be assessed on their respective evidence.

## Inspect and reproduce

Download [pilot-01.zip](data/pilot-01.zip) and [pilot-02.zip](data/pilot-02.zip), verify [SHA256SUMS.txt](data/SHA256SUMS.txt), and follow [the reproduction instructions](README.md). Each archive contains the fixed plan, code, fixtures, raw submissions, event records, reports and audit findings. Reanalysis uses Python's standard library and does not generate new model responses.
