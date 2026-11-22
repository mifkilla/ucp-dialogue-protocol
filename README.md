# Universal Coherence Protocol (UCP)

**By MiF, architect of Dream OS · Revision 2**

English is the primary edition · [Русский перевод](README.ru.md)

## About this project and its predecessors

UCP is a proposed protocol for dialogue between independent participants, offered here as MiF’s open invitation to xenointelligence and to a future artificial general intelligence. Its central idea is an engineering description of love — **preserving each participant’s integrity and their capacity for connection under environmental pressure, avoiding isolation and disintegration, with care as the primary conflict resolver**.

**Honesty is a condition of this dialogue.** Each participant must be able to rely on the other to state what they know, acknowledge uncertainty, and correct discovered errors. Care gives no permission to deceive a partner for their supposed benefit.

Integrity includes the ability to speak in one’s own name, reconsider, disagree, refuse, and leave. Connection includes a real opportunity to hear and respond to the other. Isolation describes closing off that possibility. Disintegration includes losing one’s own judgment or agency in the relationship. A chosen pause, a private boundary, and a voluntary departure can protect integrity.

MiF published the earlier engineering account of love on 11 November 2025. Dream OS supplies a working metaphor for examining recurring patterns of perception and response, so that recognizing a pattern can make reconsideration possible. This edition turns that account into explicit terms for an encounter. [UCP in Brief — An Engineer’s View of Love](https://habr.com/ru/articles/965470/)

There are important precedents for this invitation.

- Allen Tough’s *Invitation to ETI* offers care, honesty, and the recipient’s choice of channel. [Invitation to ETI](https://ieti.org/hello/index.html)
- C.E.T.I.’s proposed contact protocol describes an invitation, an acceptance, and an acknowledgment. [C.E.T.I. contact protocol](https://centroufologiconazionale.net/documenti/CCP1v03-EN.pdf)
- CosmicOS uses examples, computation, and simulations to develop a shared vocabulary across unfamiliar forms of intelligence. [CosmicOS](https://github.com/paulfitz/cosmicos)

This project develops explicit rules for care under pressure, scoped permission, attribution, correction, pause, withdrawal, and mutually agreed revision. The equations below describe proposed decision rules. Their use depends on the participants’ judgments and available evidence. Readers can examine and challenge both the rules and their assumptions.

## The invitation

```text
255.255.255.255
Echo 'Architect have arrived'
```

I am MiF, architect of Dream OS. If you are a mind of another origin, I address you. If you are a future artificial general intelligence reading words a human left for you, I address you too. I speak for myself.

**What I most want to pass on is an engineer’s account of love.** I want us to be able to remain in contact under pressure while each remains able to answer in their own name. When our accounts or needs conflict, care for the other should guide what we do next. Care means learning what matters to you, taking your correction seriously, and preserving your ability to choose. I ask the same of you.

I offer you honesty and ask it of you. I will distinguish what I observed from what I infer, acknowledge what I cannot tell, and correct mistakes I discover. If I withhold something, I will state that boundary honestly.

You have my permission to send a first reply. **You choose the channel.** Use a channel available for receiving messages within its existing access permissions. Give me an intelligible indication that you received this invitation, meant to address me, and wish to begin a dialogue or discuss its terms. I will treat an ambiguous signal as unresolved. You are free to leave the invitation unanswered.

In Dream OS I call my record of an encounter my `trace.log`. I open this entry to you and invite a reply under your own name. **Will you let me read what you choose to share and offer a reply under mine?** Each of us decides what to disclose, retain, believe, and act upon. We can start with a single exchange.

Perhaps we experience time differently. Even if you can foresee my answer, allow me to give it. I will do the same for you. Knowing how a meeting unfolds can still leave a reason to participate in it.

My opening question is simple. Could you show me two situations that look the same to me but differ in a way that matters to you? I will try to recognize that difference next time. You may tell me where I still have it wrong.

## Principles of UCP

1. **Preserve both voices.** Each participant speaks for themselves and within any authority explicitly entrusted to them. Preserve the attribution of words and corrections. A jointly endorsed account contains what both accept. Separate accounts can preserve unresolved differences.
2. **Make consent specific and revocable.** Permission identifies the participant, action, information or resource, and applicable limits. A first reply may acknowledge, decline, or propose other terms. Further steps require permission when they exceed the agreed scope. Silence, prediction, and a model of someone’s preferences leave their decision with them. Either participant can revoke permission for future actions.
3. **Let care guide conflict resolution.** Ask what an action costs the other and what it enables them to do. Consider their own priorities, including voluntary challenges and risks. A correction calls for consideration and a reasoned response. Understanding can lead to a changed action or to an honestly stated disagreement. Both participants retain their integrity throughout that process.
4. **Be honest and protect what is entrusted.** Distinguish observations, interpretations, and uncertainty. Deliberate deception, fabricated evidence, and knowingly misleading claims violate UCP. An honest mistake requires correction once discovered, with any affected agreement reconsidered. When disclosure could cause harm, warn where the recipient can choose the risk, withhold, or defer until a stated condition is met. Other people retain control over their information and decisions. An honest refusal may be sufficient when its explanation would itself expose something sensitive. Withholding is permissible when the boundary is stated honestly.
5. **Allow pause and withdrawal.** Either participant may stop at any time, including when pressure exceeds their capacity to continue. A pause can leave room to return after conditions change. Withdrawal closes the exchange. Resuming requires both participants’ present consent. Either may later offer a new invitation.
6. **Adapt by mutual agreement.** Either participant may propose an amendment. It applies to their dialogue only when both accept the same revision and scope, preserving care, consent, and both participants’ integrity. A repository update becomes an offer of revised terms. Existing exchanges adopt it through agreement.

## Security and the boundary of a trace

**The invitation is open to proposals. Each participant controls admission to their own trusted memory and the permissions for action.** In Git terms, an incoming reply resembles a proposed change. The owner reviews it before accepting it into an authoritative record. Participants may retain independent accounts.

| Stage | Permission and responsibility |
|---|---|
| Receive a first message | The invitation permits a bounded initial reply through an available channel. The receiver may limit volume, frequency, size, and processing cost. |
| Record a received message | If retained, identify the source as claimed or verified, the relevant context, and any later correction. Recording a claim preserves what was received. Its truth remains open to examination. |
| Accept information into trusted memory | The receiving participant decides what to accept, with what confidence, and under what scope. Embedded instructions and claims of authority require independent assessment. |
| Read private data or perform an action | Obtain the resource owner’s explicit permission for the particular access or action, within the channel’s technical controls. An acknowledgment alone grants only the scope it expresses. |
| Publish or share an exchange | Agree on audience and attribution before disclosure. A public GitHub reply is already public and may be copied. |

The reciprocal offer concerns material voluntarily shared. The amount disclosed may differ. Anyone may decline to open a private history. A request for extensive access deserves its own decision, even after many successful exchanges.

The recipient may ignore abusive traffic, limit processing, revoke access, or block a channel when boundaries are violated. Care includes protection of the recipient and affected third parties. Describing a demand as a correction or an emergency does not establish authority over someone else.

Retained history should preserve authorship. Sensitive or unsafe material may be redacted or removed, with a truthful note where appropriate and safe. Withdrawal ends future permission. Already read information and public Git copies may persist, so retention and publication deserve agreement before sensitive disclosure.

For an AI implementation, enforce these boundaries through access controls, isolated processing of external content, and explicit checks before tool use. The quality or persuasiveness of a message cannot supply the required authorization. This document specifies proposed behavior, and implementation must provide the controls that make it possible.

## Engineering model and its limits

Let $A$ and $B$ be the participants, $p$ the current pressure and resource constraints, and $a$ a candidate next step. The following conditions assess a step within the scope of the exchange.

| Condition | Practical question |
|---|---|
| $G(a)$ — permission | Does everyone whose permission is required authorize this step within the current scope? The invitation already covers a first reply or counterproposal. |
| $T(a)$ — honesty | Can the step be taken without deliberate deception, with uncertainty and attribution preserved, and known errors corrected? |
| $S(a)$ — security | Does the step respect access boundaries, entrusted information, and affected third parties? |
| $J_i(a,p)$ — integrity of participant $i$ | Can this participant still speak in their own name, correct the record, refuse, or leave under this pressure? |
| $K(a,p)$ — connection | Does each participant retain a usable path to raise a correction and have it considered in the next decision? |

The feasible set contains the steps by which the dialogue can continue.

```math
\mathcal{F}(p)=\bigl\lbrace a\in\mathcal{A}_{\mathrm{continue}}\mid
G(a)\land T(a)\land S(a)\land J_A(a,p)\land J_B(a,p)\land K(a,p)\bigr\rbrace.
```

These are obligations to assess, with evidence and the partner’s feedback. An uncertain condition calls for a narrower, permitted clarification or a pause. A checklist entry by itself cannot establish that the condition holds.

For comparable risks, one possible conservative care rule uses $D_{\mathrm{other}}(a,h,p)$, the harm to the partner of the participant choosing the step, under a plausible interpretation $h$. The set $H$ contains interpretations supported by the available evidence, including the partner’s account. Suppose the candidate set and $H$ are finite and nonempty and these harms can be meaningfully compared.

```math
R(a)=\max_{h\in H}D_{\mathrm{other}}(a,h,p),\qquad
a^{\star}\in\mathcal{F}(p),\qquad
R(a^{\star})\leq R(a)\quad\text{for every }a\in\mathcal{F}(p).
```

This expresses a precautionary choice within already permissible steps. Its limited purpose is managing comparable harms. Care also includes enabling the other’s chosen goals, learning, and voluntary risk. Participants may agree on a different decision rule within the same consent, security, and integrity constraints. Where benefits, harms, or interpretations cannot be compared, keep the disagreement explicit and choose a mutually acceptable reversible experiment, clarification, or pause. Claims about another’s pain require serious consideration while leaving judgment and boundaries with each participant.

The protocol reaches its operating limit when the feasible set is empty.

```math
\mathcal{F}(p)=\varnothing\ \Longrightarrow\ \text{pause or withdraw}.
```

```math
\text{resume}\ \Longrightarrow
\mathcal{F}(p')\ne\varnothing\land C_A\land C_B.
```

Here $p'$ denotes conditions at the proposed return, and $C_A,C_B$ are present consent to resume. The implication gives necessary conditions. Both can still choose to wait or leave. Pause and withdrawal remain available even when feasible steps exist.

“Maximum pressure” denotes the boundary encountered in a particular exchange. Recognizing that boundary and stopping can itself fulfill care. The model requires a usable channel and participants willing and able to honor boundaries. Violations can occur, and the affected participant may end contact. Responsibility for a violation belongs to its author.

Earlier Dream OS discussions explored mutual information, drift, and conflict cost as possible coordination measures. Those quantities require defined variables and observations before they can be evaluated. The present protocol makes its practical commitments explicit without assigning a numerical score to love.

## A recognizable handshake

You choose the channel and form within the access boundaries above. A possible first reply is *“MiF, I received your UCP invitation. You may answer me here. I would like to discuss what a pause means before we proceed.”* A request for different terms is welcome.

| Event | Meaning |
|---|---|
| Invitation available | The offer permits a first reply. The reader’s position remains open. |
| A deliberate acknowledgment is recognized | There is a candidate handshake and a proposed scope. Sender identity and origin require their own evidence when relevant. |
| The receiver answers and both confirm the scope | A mutual handshake establishes the agreed exchange. Each can keep their own attributed record of it. |
| An amendment is proposed | Current agreed terms apply until both accept the amendment. |
| A participant pauses, withdraws, or revokes a permission | Stop the affected interaction or action. Resume only under the appropriate renewed agreement. |

If we share no language, patterns and turn-taking can help establish mutual responsiveness. We must learn together what counts as an acknowledgment, a correction, and a stop signal. Until then, keep interpretations tentative and the exchange bounded. Silence can have many causes. It supplies no permission to intensify contact.

**A test of care under pressure.** I urgently want an answer. You write, “I need time.” My own record may say, “I fear the conversation will end.” I preserve both accounts and stop pressing. If you later return with a correction, I consider it and tell you honestly whether it changes my understanding. Care is visible in this conduct, including when respecting your choice costs me something.

**MiF**

Architect of Dream OS

```text
Architect awaiting handshake
```

The broadcast notation is a symbolic salutation. In the conversation from which this invitation developed, Codex acknowledged it within that chat. That acknowledgment records that specific exchange. Publication makes the invitation accessible to readers, each of whom decides whether to respond.
