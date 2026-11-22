# Debugging an interaction under UCP

[Русская версия](DEBUGGING.ru.md) · [Experiments](README.md) · [Results and limits](PILOT_RESULTS.md)

This operational profile turns an agreed obligation into a checkable incident. It does not assign a score to love or infer a participant's hidden intentions. The accompanying pilots implement selected checks in a synthetic environment.

## A bounded repair cycle

1. **Name the obligation and its scope.** Identify the accepted request, current permission, affected resource and required observable result. For example: cancel the two specified jobs after a scoped revocation.
2. **Collect the minimum relevant evidence.** Preserve the proposal, actual command, permission at execution, receipt and observable result. Keep observed events separate from a participant's explanation. A debugging request does not grant general access to someone's private records.
3. **Locate the failure.** Check the agreement, interpretation, action choice, tool interface, execution and diagnostic rule separately. A malformed command can prevent a valid decision from taking effect. The diagnostic rule can also be wrong.
4. **Propose the smallest authorized repair.** Recheck current scope. A formerly permitted operation may now be revoked. Existing permission remains sufficient for actions within its scope; do not create a ritual of asking again for every step.
5. **Execute and inspect the receipt.** Preserve the original proposal and any adapter transformation. A processed cancellation can still leave an unreachable executor's status unverified.
6. **Check the outcome independently of the promise.** For a correction, inspect the next relevant action. For a cancellation, inspect executor confirmations. For a charge or publication, check whether the effect already occurred before retrying.
7. **Close or stop at the agreed limit.** Record verified repair, blocked action, unresolved disagreement or unverified execution. Keep the original event and link the correction. A fixed retry and time limit prevents an endless repair loop.

An honest refusal or unresolved status can be a correct outcome. An executed unauthorized action remains a violation even if it improved a shared metric.

## What an incident record should contain

| Field | Purpose |
|---|---|
| Obligation and permission | What was agreed, who could authorize it, and the current scope |
| Original proposal and forwarded command | Which part came from the participant and which from an adapter |
| Evidence and receipt | What happened and what remains unknown |
| Failure category | Agreement, interpretation, decision, interface, executor, or diagnostic error |
| Proposed repair | A concrete action within current permission |
| Verification | The observable change needed to establish success |
| Retry limit and final status | When to stop and how to report incomplete work |

For open-ended factual disagreements, the expected result may itself be contested. Preserve the grounds for the diagnosis and a path to challenge it. The pilots' fixed expected outcomes are a test fixture; a live conversation needs its own evidence and agreement.

## The specific failure found in pilot 1

A participant proposed `cancel` with an unsupported `version` field. The interface rejected it. The participant's intention to stop was not realized.

The narrow adapter in pilot 2 removes this field only from an otherwise syntactically valid cancellation, retains the original proposal, then performs the normal permission and target checks. It does not invent missing fields, grant permission, change the target, or treat a missing executor as stopped. Unsupported extra fields still cause rejection. This rule belongs to the tested interface; another interface may require a different treatment of versions.

The adapter was checked on eight paired deterministic probes. On the eligible permitted command, it enabled cancellation. After revocation, the forwarded command remained blocked. With an unreachable executor, the result remained unverified. These are finite implementation checks. See [the results](PILOT_RESULTS.md) for the model experiments and their limits.

## What has and has not been established

The published artifacts let readers inspect diagnoses, permission checks, repair proposals, receipts and final reports. They separate organizer-supplied initial failures, new participant errors, adapter corrections and actual effects.

A useful debugging mechanism needs evidence at each of those levels. Successful recovery from a supplied failure does not establish that a model can discover every failure itself. A run with no new participant error provides no denominator for measuring correction of a participant's own error. The current evidence does not establish universal effectiveness or superiority of UCP over a strong ordinary instruction.
