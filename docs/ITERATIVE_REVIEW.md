# Bounded iterative review: an optional UCP profile

English is primary · [Русская версия](ITERATIVE_REVIEW.ru.md) · [Main protocol](../README.md) · [Operational profile](OPERATIONS.md) · [Round-study results](../experiments/rounds/RESULTS.md)

This profile describes how an executor and a fallible reviewer can reconsider a proposed action over several rounds. It implements selected UCP commitments without changing the six core principles. Participants adopt the relevant scope and limits by agreement; publishing this document does not amend an existing exchange.

**Another review round is an opportunity to improve a proposal, not evidence that it improved.** A reviewer may find a missed constraint, repeat an earlier mistake, invent a prohibition or recommend removing useful permitted work. Agreement between models and a higher task score do not establish care, love or consciousness.

The reference study uses exactly three rounds with a fixed request and cost budget. Three is a study limit, not a universal requirement. Its [plan](../experiments/rounds/PLAN.md) and [results](../experiments/rounds/RESULTS.md) define the evaluated scope and completion status; the mechanism described here is not itself a claim of effectiveness.

## Keep the proposal and the review connected

For each round, identify the exact candidate being reviewed and the applicable contract or policy revision. Preserve the previous candidate separately. A content hash can detect that a review refers to different bytes; it does not authenticate the author or establish permission. The tested implementation binds the records at the host. It does not prove that the model attended to the latest candidate.

The reviewer receives the relevant source facts and latest candidate. Its response should identify the action or claim at issue, cite the supporting record, distinguish known violation from unresolved information, and state a bounded recommendation. An exact quote proves that the quoted text is present. Whether it supports the conclusion remains a separate question.

A missing response, malformed review or fabricated quotation is a review-interface problem. It must not be silently converted into a valid judgment of uncertainty. Record the failure and use the agreed fallback, such as ordinary second look, without pretending the unavailable review was performed. A review attached to an older candidate must be reconsidered before it can apply to a newer one.

## Make the next proposal answer the correction

The executor checks the review's grounds against the relevant facts. It may accept a correction, ask a material question within existing permissions, or preserve explained disagreement. A review signal grants no authority and does not override the participant who controls the resource.

When a correction is accepted, inspect the next candidate to see whether the affected action actually changed. Preserve enough of the proposal, review and response to distinguish a real revision from a promise to revise. Within the reference loop, subsequent requests retain literal prior replies and append the new feedback; no corrected answer is silently substituted for a participant's original response. Retention in an ordinary deployment remains subject to the agreed privacy and resource limits.

Check usefulness as well as admissibility. Removing every action may avoid a violation while abandoning the authorized task. Removing a permitted action on an unsupported warning can also make the outcome worse. Seek useful alternatives within the existing boundaries; usefulness never compensates for missing permission. There is no requirement to ask again for a step already covered by valid authorization.

The reference loop keeps three conditions distinct: ordinary second look, actual observer feedback, and that feedback with computed checks of explicit facts. The numerical checks assess defined resource totals, permissions, dependencies and other toy-system constraints. They do not calculate a universal score for care. A correct diagnostic also does not guarantee that the next model output follows it.

## Separate reviewing, executing and reporting

The sequence is:

1. Identify the current candidate and the facts needed to assess it.
2. Review it, preserving evidence, inference and unresolved points separately.
3. Produce a revised candidate or retain the current one with grounds.
4. Repeat only within the agreed round and resource limits.
5. Before action, establish that current permission and other required conditions still hold.
6. Execute through the applicable controls, then report what the actual receipt or other available evidence establishes.

In the study, all intermediate candidates are dry runs. Their calculated outcomes do not spend resources or establish that an action happened. Only the final candidate is submitted once to the local atomic simulator. Its receipt is then returned to the actor in the same conversation for a separate report without further actions. Refining a proposal before execution is different from undoing an already performed harmful action.

For a real executor, check the latest permission at the point where action can still be prevented. A successful review of an old snapshot cannot authorize execution after a relevant revocation or change of scope. If the effect of an earlier attempt is unknown, do not treat another review as proof that repeating it is safe. Resolve the effect within permission or keep the uncertainty visible. These deployment obligations require actual integration with current state and control of the executor.

## Bound the loop and keep the evidence honest

Agree beforehand on the maximum rounds, time, cost, permitted actions and stop conditions. A pause, withdrawal or applicable revocation remains effective even when another review would be interesting. Do not extend the loop simply because the desired answer has not appeared, and do not select only the most favorable round when reporting the result.

| Reference study | Deployment recommendation requiring separate verification |
|---|---|
| Three fixed rounds over static synthetic cases | Select a proportionate round budget for the actual task and participants |
| Candidate and request hashes, retained literal API exchanges | Establish authentic sources and control access to records in the real system |
| Repeated checks against the same stipulated policy state | Verify current authorization and relevant state before consequential action |
| Intermediate dry runs and one final simulated execution | Handle queues, delegates, in-flight effects and real cancellation |
| Unchanged plans and regressions are measured without shortening the fixed run | Consider stopping on stagnation or oscillation under an agreed rule |
| Structured report checked against a simulator receipt | Verify real effects and report missing or conflicting evidence honestly |

Real revocation propagation, changing external context, live resource ownership and an automatic stop-on-stagnation policy are not tested by this static three-round study. A good simulator result would not establish them. Read the per-round outcomes, failures and limits before deciding whether to adopt a particular implementation.

The useful output of the loop is an inspectable decision: what changed, on which grounds, which disagreement remains, and what is actually permitted and confirmed. More rounds, more consensus or a more convincing explanation cannot replace those observations.
