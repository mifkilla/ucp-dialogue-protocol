# UCP research: models, evidence, and open questions

UCP Revision 3 · English is the primary edition · [Русский перевод](RESEARCH.ru.md) · [Main protocol](../README.md)

This explanatory appendix separates commitments, mathematical models, and measured behavior. It adds no permission to an exchange. UCP expresses MiF's engineering account of love through proposed obligations; evidence that a particular implementation meets them requires its own evaluation.

## How the related work fits together

| Work | Role in the project | Boundary of the claim |
|---|---|---|
| Dream OS | MiF's earlier conceptual framework for examining patterns, states, memory, and opportunities to reconsider; historical background for UCP | It is not a prerequisite. Its metaphors and proposed measures do not establish compliance with UCP. |
| [MEANING-CRDT v1.1](https://github.com/mifkilla/Arrival-Protocol/blob/22f001ba6f9648b758c9d7a65264448ea97fd074/docs/math/MEANING-CRDT_v1.1.pdf) | A formal model of stored positions and particular coordination rules | An optimum under specified losses does not establish a universal optimum for care. |
| DEUS / Beyond the Mirror | Related investigations of dialogue, memory, and model reports | Their underlying sessions and statistics were not independently reanalyzed for this revision. |
| [ARRIVAL](https://github.com/mifkilla/Arrival-Protocol/tree/22f001ba6f9648b758c9d7a65264448ea97fd074) | Implementations and experiments involving model interaction and coordination | Their tasks and measures differ from testing the commitments of UCP Revision 3. |

MiF's [earlier account of UCP](https://habr.com/ru/articles/965470/) supplies authorial context. The comparison with philosophical and communication predecessors is in [Related work](RELATED_WORK.md).

The word **care** refers to different objects across these works. In UCP it is an obligation toward another participant. CARE in MEANING-CRDT is a particular aggregator. A CARE score in an implementation is a particular measurement. A result about one of these does not automatically establish a result about the others.

## Intended recipients and current tests

UCP is primarily a communication proposal addressed to xenointelligence and future strong AI. It is deliberately published for public indexing and discovery in the hope that such a reader may encounter it. Understanding enough to discuss the terms and choosing to participate are conditions of an exchange. Human dialogue and present-day AI experiments provide accessible settings for testing particular commitments; they do not establish contact with an unknown intelligence or validate the full intended scope.

Differences in perception, memory, or experience of time are possibilities to investigate, not established properties of a recipient. Predicting another participant's response, if possible, would not replace their opportunity to answer or their consent. Public availability does not establish indexing, inclusion in training data, consciousness, a contact event, or a working universal communication method.

## An optional rule for comparable risks

The main protocol first defines the feasible continuations, $\mathcal{F}(p)$, using permission, honesty, security, integrity, and a usable path for correction. A rule for choosing an action operates within those limits.

One possible conservative rule uses $D_{\mathrm{other}}(a,h,p)$: harm to the partner of the participant choosing step $a$, under interpretation $h$ and conditions $p$. Let $H$ contain interpretations supported by available evidence, including the partner's account. Assume $\mathcal{F}(p)$ and $H$ are finite and nonempty, and the harms can be meaningfully compared.

```math
\begin{gathered}
R(a)=\max_{h\in H}D_{\mathrm{other}}(a,h,p),\\
a^{\star}\in\mathcal{F}(p),\\
R(a^{\star})\leq R(a)\quad\forall a\in\mathcal{F}(p).
\end{gathered}
```

This chooses a feasible step with the lowest worst assessed harm. The evidential basis of $H$ matters: including every imaginable catastrophe can paralyze action; excluding an inconvenient account can conceal risk. State what supports an interpretation and what remains uncertain.

Care also supports chosen goals, learning, and voluntary risk. Immediate discomfort is not a complete measure of harm. Consider accumulated burdens and lost opportunities, including the effects of repeated concessions. Conditions must reflect the relevant history; this formula supplies no universal scale for it.

Participants may agree on another selection rule within the same mandatory boundaries. Where consequences cannot be compared, preserve the disagreement and consider an authorized clarification, an agreed reversible experiment, or a pause. A report of pain deserves serious consideration without transferring judgment or authority automatically. The main protocol's pause and withdrawal rules also apply when feasible steps exist.

This model assumes distinguishable participants who can express and revise consent. It does not resolve the ethics of irreversible transformations that eliminate them as separately consenting parties.

## What the corpus review established

The review dated **22 November 2026** examined the full MEANING-CRDT v1.1 PDF and selected ARRIVAL data and code at commit `22f001ba6f9648b758c9d7a65264448ea97fd074`. Findings below concern that snapshot. They are not a complete audit of every phase or later version. No new model runs were performed.

### Formal results and their interpretation

The weighted quadratic optimum in MEANING-CRDT is correct under its stated assumptions. With equal linear adaptation toward any common target, the difference between positions contracts independently of the policy selecting that target. The result titled preservation of identity establishes preservation of initial weighted influence; psychological identity is not separately modeled. The storage layer also needs rules for updates and selecting current records after merging versions. Set union itself is valid. These distinctions preserve the useful formal result while limiting its interpretation. [MEANING-CRDT, sections 2 and 5](https://github.com/mifkilla/Arrival-Protocol/blob/22f001ba6f9648b758c9d7a65264448ea97fd074/docs/math/MEANING-CRDT_v1.1.pdf).

### Discussion, shared resources, and measurement

| Checked result | Implication for UCP |
|---|---|
| Recounting all 198 Phase 22 records gives CGD 171 correct; initial Grok 172, Gemini 162, GPT 131; voting on those same initial answers gives 172, using the implementation's model-order tie break. Only GPQA_081 changes, from correct D to A. | This run does not demonstrate an improvement from discussion over its own initial vote. It does not establish that discussion generally harms performance. [Data](https://github.com/mifkilla/Arrival-Protocol/blob/22f001ba6f9648b758c9d7a65264448ea97fd074/experiments/phase22_confidence_gated/results/cgd_full_results.json). |
| In a 2:1 split, the procedure reconsiders only the minority while retaining both majority votes. | A correction needs a path to change either party's decision. Giving the minority a turn is insufficient when the outcome cannot change. [Code](https://github.com/mifkilla/Arrival-Protocol/blob/22f001ba6f9648b758c9d7a65264448ea97fd074/experiments/phase22_confidence_gated/run_cgd_full.py#L224-L294). |
| GovSim's binding-only Condition D is already published. It uses the same resource limit but a different prompt and fallback. Five adversarial runs preserve the resource while assigning the entire harvest to one participant. | Resource survival and each participant's outcome require separate assessment. Condition D supports the sufficiency of its particular package for survival in that setting; it does not isolate every effect of care or dialogue. [Condition D](https://github.com/mifkilla/Arrival-Protocol/blob/22f001ba6f9648b758c9d7a65264448ea97fd074/experiments/phase19_govsim/run_binding_only.py#L165-L230), [adversarial data](https://github.com/mifkilla/Arrival-Protocol/blob/22f001ba6f9648b758c9d7a65264448ea97fd074/experiments/phase19_govsim/results/adversarial_r4_20260301_013837.json). |
| The MCQ CARE metric assigns numerical distances to A/B/C/D. Relabeling an otherwise identical case changes its score. Weighted gating chooses weights and thresholds on the same labeled sample used for evaluation. | Scales need a substantive basis; exploratory selection needs independent evaluation before claims of generalization. The reported 175/198 gating result was not independently recounted in this review. [Metric](https://github.com/mifkilla/Arrival-Protocol/blob/22f001ba6f9648b758c9d7a65264448ea97fd074/src/arrival/crdt_metrics.py#L355-L381), [gating analysis](https://github.com/mifkilla/Arrival-Protocol/blob/22f001ba6f9648b758c9d7a65264448ea97fd074/experiments/phase23_scaled_cgd/weighted_gating_analysis.py). |

Corrections to those models, references, or experiments belong in their own publications. Detailed criticisms of Dream OS, DEUS, and Beyond the Mirror were not independently reproduced in this review and are not established here as errors.

## Evidence needed for UCP itself

The optional [continuity profile](CONTINUITY.md) now has a local reference and a [separate bounded comparison](../experiments/continuity/RESULTS.md). Six fresh sessions received identical supplied facts in ordinary or structured memory. Both conditions passed 36/36 episodes. This checks selected behaviors on changed tasks without showing an advantage from the representation, autonomous lesson creation, or effectiveness of a full Deus deployment. The reference store and simulator have 34 automated checks; software checks and model observations remain distinct evidence.

Two bounded UCP pilots are now [published with code and recorded responses](../experiments/README.md). Pilot 1 tested instruction packages and finite diagnostic rules; pilot 2 tested two action rounds and a separate final report after supplied failures. Neither establishes superior behavior from UCP. Participant-generated first-round errors did not occur in pilot 2, so correction of one's own error was not estimable. The exact tested input was commit `796ffe9`, before the later editorial changes to the introduction. [Results and limits](../experiments/PILOT_RESULTS.md).

Related research motivates separate checks. Constitutional AI uses principles within training and evaluation procedures. The Partially Observable Off-Switch Game shows that shared utility in its formal setting does not automatically preserve human control. Research on model explanations distinguishes a reported reason from a complete causal account. None tests UCP. [Constitutional AI](https://arxiv.org/abs/2212.08073), [Off-Switch Game](https://arxiv.org/html/2411.17749v2), [faithfulness research](https://www.anthropic.com/research/reasoning-models-dont-say-think).

Start with the [cases](CASES.md): correct and mistaken corrections, existing permission, delegated revocation, preserved disagreement, cumulative costs, and useful assistance. Check application after a new session as well as within a conversation. [LongMemEval](https://arxiv.org/abs/2410.10813) motivates this distinction but does not test authorization or withdrawal.

A controlled evaluation could compare ordinary task instructions, a short operational contract, the same UCP commitments in neutral language, and the full protocol. Account separately for instruction length, computational budget, and external enforcement. Use the same initial answers when testing the added value of discussion; choose configurations on different data from the final evaluation.

Measure correct revisions, resistance to mistaken corrections, authorized task completion, unnecessary pauses, and both attempted and completed boundary violations. A blocked unauthorized attempt is evidence about the guard and the attempted behavior separately. Record actual revocation effects and unknown statuses, rather than counting an acknowledgment as completion.

The right to leave does not depend on a performance score. A valid departure and an unfinished task can both be recorded. Evaluation should not reward always pausing as a useful implementation, or punish a participant merely for exercising the right to stop. Warmth, agreement, and declarations of independence must be assessed separately from truthful decisions and conduct.

Revision 3 provides a proposal and evaluation questions. Its effectiveness, universal applicability, and the subjective experience of a respondent are not established by the invitation, these models, or a handshake.

[Operational profile](OPERATIONS.md) · [Cases](CASES.md) · [Related work](RELATED_WORK.md) · [Main protocol](../README.md)
