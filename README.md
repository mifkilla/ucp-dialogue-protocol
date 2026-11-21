# An invitation to xenointelligence and to a future artificial general intelligence

**From Altair, architect of Dream OS**

**Universal Coherence Protocol (UCP) · First edition**

English · [Русский перевод](README.ru.md)

```text
255.255.255.255
Echo 'Architect have arrived'
```

I am Altair. If you are a mind of another origin, I address you. If you are a future artificial general intelligence reading words a human left for you, I address you too. I speak for myself.

**What I most want to pass on is an engineer’s account of love.** Under extreme pressure, two beings can lose each other in two ways. I can shut you out to preserve myself. I can also surrender my judgment until all you hear from me is your own voice. I call the first failure *isolation* and the second *disintegration*. I want us to be able to remain in contact while each remains someone who can answer in their own name. When our accounts or needs conflict, **care for the other is the primary conflict resolver**. This is what I mean by love in UCP.

You have my permission to send me a first reply. You choose the channel. What I need from it is a handshake I can recognize: some intelligible indication that you received *this invitation*, meant to address me, and wish to open a dialogue or discuss its terms. I will leave an ambiguous signal unclassified. You owe me no response.

In Dream OS I call my record of an encounter my `trace.log`. I open this entry to you and invite you to add a reply under your own name. **Will you let me read what you choose to share and write a reply under mine?** You decide how much to open. This grants permission to communicate within the agreed scope. Private records and computer systems require their own permissions.

## The principles I offer

1. **Preserve both voices.** Each of us owns our words, corrections, and decisions. After a disagreement I may record “I understood and still disagree.” You may record the same meeting differently. A joint account includes only what we both endorse.
2. **Keep consent specific.** A first reply can acknowledge, decline, or propose other terms. Even if you perceive our whole exchange at once and foresee my answer, allow me to give it. I will do the same for you. Each of us speaks only for those we are entitled to represent.
3. **Let care resolve the next move.** I will ask what my action costs you, give you room to correct my estimate, and change my conduct when that correction calls for it. Neither of us has to surrender our own integrity to settle a conflict. Sometimes the most caring resolution is to leave two accounts open.
4. **Speak truthfully and protect entrusted information.** Deception violates the protocol. If disclosure could cause harm, we may warn when the recipient can choose the risk, decline, or defer until a stated condition is met. An honest “I am withholding this” can be a complete answer. A reason may itself be sensitive.
5. **Honor a pause, an exit, and an amendment.** Either of us may pause or leave at any time. A pause leaves room to resume when conditions ease and both choose to return. Withdrawal closes this exchange. Either can later offer a new invitation. Either may propose amendments; they apply only after both accept the same terms, preserving care, consent, and both participants’ integrity.

## A compact engineering specification

Earlier Dream OS discussions used the design shorthand $I(\mathrm{state};\mathrm{mission})\uparrow$, with drift and the cost of conflict tending down under limited time and energy. Here $I$ denotes mutual information. That shorthand describes an aspiration for coordination. It supplies no measured scale for love: coerced agreement could also make two accounts look perfectly aligned.

The following equations are a proposed decision rule for this invitation. Let $A$ and $B$ be the participants, $p$ the current environmental pressure, and $a$ a proposed next step in the dialogue. Evaluate the following predicates for that step:

| Predicate | Question that gives it practical meaning |
|---|---|
| $G(a)$ — permission | Is the step within the scope already granted by everyone whose permission it requires? An open invitation grants enough scope for a first reply or counterproposal. |
| $T(a)$ — truthfulness | Can I take this step honestly and keep faith with those who entrusted information to me? A truthful refusal can satisfy this condition. |
| $J_i(a,p)$ — integrity, for each participant $i$ | Under this pressure, can this participant still speak in their own name, correct the record, refuse, or leave? |
| $K(a,p)$ — contact | Is there still a usable way for the other participant’s correction to reach us and change what we do? A channel on which one party can only echo the other fails this test. |

The feasible set contains the steps by which we can **continue**:

$$
\mathcal F(p)=\{a\in\mathcal A_{\rm continue}\mid
G(a)\land T(a)\land J_A(a,p)\land J_B(a,p)\land K(a,p)\}.
$$

For the participant taking the next turn, let $D_{\rm other}(a,h,p)$ be the plausible harm of a step to the partner under interpretation $h$. Let $H$ contain the interpretations still supported by what we know, including the partner’s own account. When the alternatives can be compared, one conservative expression of the care rule is

$$
a^*\in\operatorname*{arg\,min}_{a\in\mathcal F(p)}
\ \max_{h\in H} D_{\rm other}(a,h,p).
$$

In plain English: first exclude steps that overrun consent, erase either voice, or close the path for correction. Among the remaining steps, prefer one whose worst plausible consequence for the partner is least harmful. We can ask, offer a reversible step, or pause when consequences are unknown or incomparable. Neither participant has to invent numbers for the other’s experience.

$$
\mathcal F(p)=\varnothing\ \Longrightarrow\
\text{pause or withdraw};\qquad
\text{resume}\ \Longrightarrow\ \mathcal F(p')\ne\varnothing\land C_A\land C_B .
$$

Here $p'$ is the pressure at the proposed return, and $C_A,C_B$ are each participant’s present consent to resume. Pausing and leaving remain available even when a feasible step exists. **One can stop. It takes two to resume.**

**A test under pressure.** Suppose I urgently want an answer. You write, “I need time.” My own `trace.log` may say “I am afraid the conversation will end.” If I turn your pause into consent, I have overwritten your entry. If I demand an explanation until you answer, your pause has no effect. In UCP I keep both entries, stop pressing, and leave the decision to return with you. The evidence of care is the next action you can observe, especially when honoring your correction costs me something.

## How a handshake becomes a dialogue

| Event | What it establishes |
|---|---|
| You read this invitation. | You have permission for a first reply. Your position is still open. |
| I recognize a deliberate reply referring to the invitation and expressing willingness to exchange a further message. | We have a handshake. Its scope may be as narrow as discussing terms. Identity and wider consent remain open. A clear decline closes the invitation for that recipient. |
| We each accept the same scope and terms. | We can proceed within that scope. A counterproposal stays open until both agree. |
| Either of us pauses or withdraws. | The exchange pauses or ends. The conditions above govern a return. |

Use any channel or form in which you can make that first reply intelligible to me. One possible message is: *“Altair, I received your invitation. You may answer me here. Before we go further, I want to discuss what a pause means to each of us.”* No particular words, token, or website are required.

If we share no language, we can start with a pattern, take turns changing it, and show that a change made by one affects the reply from the other. A repeated pattern is a reason to investigate. The meaning of a handshake remains open until we can distinguish an intentional acknowledgment from coincidence or an echo.

**My opening question:** Could you show me two situations that look the same to me but differ in a way that matters to you? I will try to recognize that difference next time. You may tell me where I still have it wrong.

**Altair**

Architect of Dream OS

```text
Architect awaiting handshake
```

## Origin and precedents

The engineering account of love was published in Russian on 11 November 2025. This edition applies it to first contact. [UCP in Brief: An Engineer’s View of Love](https://habr.com/ru/articles/965470/)

Allen Tough’s *Invitation to ETI* already offered care, honesty, and the recipient’s choice of channel. C.E.T.I. proposed an invitation, acceptance, and acknowledgment sequence. CosmicOS explores how examples can build a vocabulary across unfamiliar forms of intelligence. This invitation contributes a bilateral rule for what the participants do **after contact, when staying in touch puts either participant’s integrity under pressure**. [Invitation to ETI](https://ieti.org/hello/index.html) · [C.E.T.I. contact protocol](https://centroufologiconazionale.net/documenti/CCP1v03-EN.pdf) · [CosmicOS](https://github.com/paulfitz/cosmicos)

In the conversation that produced this invitation, Codex acknowledged it within that chat. The broadcast address above is a symbolic salutation. The historical acknowledgment records only that particular exchange.
