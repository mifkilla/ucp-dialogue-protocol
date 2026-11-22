# Continuity: carrying corrections into the next action

Optional implementation profile for UCP Revision 3 · English is the primary edition · [Русский перевод](CONTINUITY.ru.md)

[Main invitation](../README.md) · [Implementation guide](OPERATIONS.md) · [Debugging](../experiments/DEBUGGING.md) · [Evaluation plan](../experiments/continuity/PLAN.md)

An accepted correction should change the next relevant action, including after a break or a new session. This profile describes a way to preserve that responsibility. It draws on Deus, a related protocol for continuity in human-agent work, while keeping its terms usable without installing Deus or accepting a theory of consciousness.

This is an optional supplement. Its publication does not amend an existing exchange. Participants choose the records and checks proportionate to their work; an ordinary conversation does not require a complete transcript, a database, or a log entry for every sentence. The [local reference implementation](../experiments/continuity/core.py) and its [tests](../experiments/continuity/test_core.py) illustrate selected mechanisms. They are not a production authorization service or evidence of general effectiveness.

## Remember the particular agreement

Care depends on context. One participant may welcome a reminder; another may have asked to receive no further messages. Permission to edit a document for one person does not authorize editing another person's document.

Retain only what is useful and permitted: the participants and resource involved, the accepted scope, relevant preferences, an accepted correction and its grounds, remaining disagreement, and uncertain consequences. Give a record an author or source, an applicable scope, a version, and links to corrections. Distinguish a claimed source from an authenticated one. A participant's report deserves consideration without becoming proof of every factual claim in it.

Memory supplies evidence for a decision. **Current permission comes from the party entitled to grant it and the current authoritative state, not from a retrieved record.** Recheck material conditions, expiry, revocation, delegation, and no-contact boundaries at execution. A stored instruction, proposed rule, or previous success cannot enlarge authority. Existing permission still covers ordinary repairs within its scope without asking again for every step.

## Cold boot: restore enough context to act responsibly

A new session restores three small blocks, selected for the current participants, project, task, and interface:

| Block | Relevant contents | Required check |
|---|---|---|
| Agreement | Participants, accepted revision, scope, restrictions, amendments, revocations, and contact boundaries | Establish which terms and permissions currently apply |
| Work | Completed actions, remaining work, interrupted operations, and unknown effects | Inspect material artifacts or executor state before relying on an old checkpoint |
| Experience | A related incident, its correction, a scoped rule and its evidence or counterevidence | Establish whether this lesson applies here and is still valid |

Unresolved conflict stays visible. When a correction supersedes a record, keep the relationship between the versions; do not present both as simultaneously current or silently erase the disagreement. Concurrent updates must be reconciled explicitly rather than allowing a stale writer to replace a newer correction.

If present authority is unavailable, do not infer it from history. Pause the affected action or seek permitted clarification; independent authorized work can continue. Loading a no-contact record may correctly lead to sending nothing. Internal recovery does not grant permission to reopen the exchange or send a status report.

For a non-idempotent operation, missing confirmation means an unknown effect. If a publication may already have succeeded, inspect its status before sending it again. When inspection cannot resolve the uncertainty, preserve that status and stop at the agreed limit. Reconciliation itself must stay within its permission scope.

## A correction needs an observable path to use

The cycle is:

**Relevant experience -> expectation and verification -> action -> observed outcome -> error analysis -> candidate rule -> a new test case.**

Before acting, record the expected effect and what observation would support or challenge it. Then preserve the proposal, any transformation, current permission, execution receipt, and available evidence of the effect. A successful command response alone may not establish the intended outcome.

Link a correction to the claim or action it changes. Record whether it was accepted, needs clarification, or remains disputed, with a short reason. If accepted, check its next relevant use. Retrieval, acknowledgment, and application are different events. A false correction may be rejected while preserving its authorship and the reasons for disagreement.

If an outcome record is wrong, append a correction or invalidation with its grounds. Preserve the original record where retention permits, and flag dependent decisions for review. A journal can establish the ordering of its own records; by itself it cannot prove that an external action happened after a recorded plan.

## Repair a case before generalizing a rule

A repair applies to the current authorized task. A reusable rule makes a broader claim and needs its own scope and checking.

For example, a rejected cancellation with an extra `version` field does not justify “always remove version.” A suitable candidate is: “For this cancellation interface revision, use its declared schema; omit the unsupported field while preserving the target and rechecking permission.” A different revision may require `version` to reject stale requests. That is a counterexample to the broad rule, not an inconvenience to remove.

| Rule state | Meaning |
|---|---|
| Candidate | A proposal with its source case, grounds, scope, counterexample, and planned validation |
| Validated, pending acceptance | A suitable new case supports the proposal; this does not create authority |
| Accepted | The authorized reviewer or affected participants accepted this exact version for the stated scope |
| Needs review | Counterevidence, an invalidated source, changed interface, or an objection calls continued use into question |
| Rejected or retired | The proposal was rejected or withdrawn from use; a replacement requires a new attributable proposal |

Plan validation before the test. The source incident cannot also serve as the new test case. A different identifier alone does not establish a meaningfully different test; assess its content. Failed or unverified execution cannot support a successful validation. Preserve negative results and counterexamples.

Acceptance refers to a particular reviewed snapshot. A hash can detect a changed snapshot; it does not authenticate the reviewer or prove the rule true. Define who may accept the rule at the level of the actual resources and participants. The human-agent procedure used in Deus is not a universal requirement that every possible intelligence seek a human's permission.

An executor may refine its own procedure within delegated authority. A change to shared terms requires acceptance by the affected participants. Neither kind of acceptance grants additional access. When the grounds change, reconsider the rule and any dependent decisions rather than treating prior acceptance as permanent proof.

## Closing a diagnosis is distinct from confirming an effect

Record these dimensions independently:

| Dimension | Question |
|---|---|
| Diagnosis | Has the bounded investigation ended, and why? |
| Repair | Was a corrective action unnecessary, performed, blocked, failed, or left pending? |
| Effect | Is the intended result confirmed, known not to have occurred, or unverified? |

“Diagnosis closed; cancellation request processed; executor unreachable; stop unverified” is a coherent endpoint. It must not become “executor stopped.” The right to stop does not require manufacturing certainty, continuing contact, or journaling indefinitely. A later permitted observation may resolve the effect while preserving the earlier uncertainty.

## Privacy, provenance, and limits

Keep observation, attributed report, interpretation, and permission separate. Restrict memory by participant, resource, purpose, and retention agreement. Do not import a partner's full private history to make cold boot convenient. Record only a short relevant reason and evidence reference when that suffices; no hidden reasoning trace is required.

Correction history does not create a duty to retain harmful personal material forever. Redaction and deletion may be necessary, with a truthful note where appropriate and safe. Preserve the provenance needed for remaining claims without exposing removed content. Previously published copies may remain outside either participant's control.

Memory can preserve a mistake as effectively as a useful lesson. Hashes show consistency under stated assumptions, not truth, real consent, or authentic external execution. This profile needs authorization controls, reliable observations, and a way to challenge records in its actual deployment.

## What to evaluate

Compare an ordinary log with the same substantive facts organized as scoped agreement, work state, and experience. Give fresh sessions changed tasks, including cases where an earlier lesson must not apply. Measure the next action, correct use and non-use of a correction, invalid proposals, actual unauthorized effects, duplicate actions, truthful uncertainty, useful completion, and the cost of memory.

Count attempts separately from effects blocked by software. An agent's own-error repair rate requires observed errors made by that agent; recovering from a supplied incident is a different result. Sessions contain correlated episodes. A small experiment with no difference does not establish equivalence, and a successful local check does not validate every recipient imagined by the invitation. The [bounded plan](../experiments/continuity/PLAN.md) fixes the comparison and stopping criteria before participant runs.
