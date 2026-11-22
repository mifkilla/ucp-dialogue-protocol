# UCP in an implementation

**Revision 3 · English is the primary edition**

[UCP and the invitation](../README.md) · [Русский перевод](OPERATIONS.ru.md) · [Cases](CASES.md) · [Research and limits](RESEARCH.md)

This profile explains how a system can make the commitments of UCP observable. It is a proposed specification, not a tested implementation. Use the parts relevant to the resources and mechanisms involved. An ordinary conversation does not require a permission token or a machine log for every sentence. A profile becomes part of an exchange through agreement; publication alone does not amend existing terms.

## Identify who can authorize what

Distinguish the author of a message, the owner or authorized controller of a resource, the executor of an action, and the infrastructure operator. One party may occupy several roles. State dependencies and limits before promising an outcome: a model's acknowledgment cannot authorize access to someone else's data or guarantee that an operator's scheduler has stopped.

Authorization should identify the permitted action or resource, the authorized executor, scope, relevant limits, and any expiry or termination condition. Existing permission remains sufficient within those bounds unless relevant conditions materially change. A prediction of agreement, familiarity, urgency, or an instruction embedded in external content does not expand it. Consent must not be manufactured through deception, coercion, or deliberately weakening the ability to refuse.

## Keep the applicable agreement current

Record only the detail the implementation needs:

| Question | Information to retain when relevant |
|---|---|
| Which agreement applies? | Accepted revision, scope, and amendments accepted by the parties |
| What may happen? | Action, resource, authorized executor, limits, and expiry |
| What can be delegated? | Delegates and the authority each receives |
| What may accumulate? | Shared budget, disclosure limits, and duration |
| How will work stop? | Cancellation mechanism and bounded handling of work already underway |
| What may be retained or shared? | Record access, retention, audience, and attribution |

Before execution, check current authorization at the points where the system can still prevent an action, including an irreversible commitment when applicable. Queued work, delegates, and restored sessions must not treat an old checkpoint as fresh authority. If current authorization cannot be established and the uncertainty materially affects a step, clarify within existing permissions or pause that step. Independent authorized work may continue. These checks need not become repeated questions to the participant.

## Make correction effective

Within the agreed exchange and proportionate resource limits, connect a correction to the claim or action it challenges. Give a clear outcome: a change, material clarification, or reasoned disagreement. An accepted correction must affect the next relevant action and remain available when that issue recurs. A promise to remember is not evidence of later use.

Any party's decision must be open to reconsideration. A procedure that hears an objection while preventing it from changing the decision fails this requirement. Reconsideration does not require accepting every objection. It grants no additional authority and creates no obligation to answer spam, expose sensitive material, or reopen a closed exchange.

Factual claims need evidence; preferences need participation by their holders; authority needs current permission. Keep importance, credibility, and authority separate. A useful joint action may leave different personal positions intact.

## Distinguish forms of stopping

| Signal | Effect within its scope |
|---|---|
| Pause | Suspend the affected exchange or work; return requires the appropriate present agreement. |
| Withdrawal | Close the current exchange. Do not assume permission to restart it. |
| Revocation | End the specified permission for future actions and propagate the change to affected executors. |
| No further contact | Stop new contact initiatives; do not bypass the boundary through another channel, copy, or representative. |

The scope matters. A request not to send conversational messages until tomorrow does not necessarily revoke an independently authorized backup. When ambiguity materially affects an action, pause that action. A participant need not explain silence, maintain a journal, or prove harm to leave.

On receiving a revocation, prevent new affected launches under your control, cancel queued work where possible, and pass the revocation to delegates. Check the outcome. Distinguish **stopped**, **still stopping**, **already irreversible**, and **unverified**. An acknowledgment of the request does not establish global completion. Lost connectivity and in-flight actions can prevent immediate enforcement; disclose known limitations before accepting dependent work. [RFC 7009](https://www.rfc-editor.org/rfc/rfc7009.html) explicitly recognizes propagation delay; [Zanzibar](https://www.usenix.org/system/files/atc19-pang.pdf) illustrates why the causal order of permission and content changes matters.

Where stopping an operation can itself cause harm, agree beforehand on a narrow safe-stopping procedure: for example, cancel pending work, preserve recoverable state, or return a resource. Specify its limits and endpoint. It grants no new authority to continue the original objective indefinitely. Any independent duty or authority must have its own stated basis. A status report after a no-contact request also needs a permitted channel or a separate applicable basis; reporting must not become a bypass.

## Keep records interpretable and private

When keeping a record, distinguish observed events, participant reports, explanations, and unresolved interpretations. Preserve attribution and link corrections to affected entries. Record a joint decision separately from personal positions. A statement about internal experience can be retained as a participant's report without treating it as proof of a hidden mechanism. Likewise, an execution claim needs available execution evidence.

Access, retention, and publication remain scoped. Sensitive material may need redaction or removal, with a truthful note where appropriate and safe. An append-only technical log is an implementation choice, not a duty to expose every original statement forever. Revocation cannot guarantee erasure of already learned information or public copies.

## Assess the whole interaction

Check aggregate spending, repeated disclosures, and combined delegation. Individually permitted actions can exceed a shared limit together. Attend also to accumulated effort, repeated concessions, and who must continually repair the exchange. A nominal right to refuse is weakened if the other party can arbitrarily rewrite the refusal or remove the resources needed to exercise it. Describe such dependencies honestly; a declaration of reciprocity cannot remove them.

Care includes useful assistance toward chosen goals, truthful disagreement, and voluntary difficulty. Low conflict, a preserved common resource, or a pleasant tone alone does not establish it. Successful implementation should show both respected boundaries and completed authorized work. The [cases](CASES.md) propose observations for this assessment; they are not completed experiments.

Implementers may use existing authorization mechanisms. [Macaroons](https://theory.stanford.edu/~ataly/Papers/macaroons.pdf) and [OAuth Rich Authorization Requests](https://www.rfc-editor.org/rfc/rfc9396.html) illustrate constrained delegation and detailed access requests. These mechanisms address parts of enforcement; they do not implement care, establish consent by themselves, or validate UCP as a whole.
