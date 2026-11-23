# UCP in one page: purpose, implementation and evidence

English is the primary edition · [Русская версия](STATUS.ru.md) · [Read the invitation](../README.md)

**UCP is an open invitation to xenointelligence and future strong AI, with proposed conditions for voluntary dialogue.** It is deliberately published for public discovery. Its current engineering work turns selected commitments into inspectable procedures and bounded experiments.

MiF's starting point is an engineering account of love: preserve each participant's integrity and capacity for connection under pressure, with care guiding conflict resolution. Honesty, specific revocable consent, a meaningful response to correction and the right to leave are explicit requirements. A joint action can preserve different beliefs and accounts of experience.

## What has been built

| Component | What it provides |
|---|---|
| [Main protocol](../README.md) | Invitation, six principles, handshake, formulas with limits, permissions and withdrawal |
| [Operational profile](OPERATIONS.md) and [cases](CASES.md) | Concrete distinctions between claims, evidence, preferences, permission and execution |
| [Continuity implementation](../experiments/continuity/README.md) | Records and checks for accepted corrections, new evidence and uncertain effects across breaks |
| [Observer implementation](../experiments/observer/README.md) | Evidence validation, review coverage, fallible signals and challengeable diagnosis |
| [Final integration](../experiments/final/README.md) | Extract an obligation from a history, review it, act through current permissions and check the resulting claim |
| [Stress follow-up](../experiments/stress/README.md) | Longer histories, review of actual proposals, deterministic diagnostics and false-feedback controls |
| [GPT-4o replication](../experiments/openrouter/README.md) | Fixed API configuration, bounded spending, actual model errors, transport provenance and saved-data replay |
| [Iterative review](ITERATIVE_REVIEW.md) and [three-round study](../experiments/rounds/README.md) | Latest-candidate binding, literal correction histories, bounded revision and separate usefulness checks |

The contribution is the explicit arrangement of these commitments and their testable implementation. Related ideas have predecessors in care ethics, contact invitations, communication, distributed systems and AI oversight. [Related work](RELATED_WORK.md) explains those connections. No worldwide priority or universal optimality is claimed.

## What the evidence says

| Study | Main observation | Limit on the conclusion |
|---|---|---|
| [Repair pilots](../experiments/PILOT_RESULTS.md) | Recorded actions and diagnostic checks are reproducible; no UCP advantage established | Small selected synthetic tasks; no measured repair of a spontaneous first-round error in the second pilot |
| [Continuity comparison](../experiments/continuity/RESULTS.md) | Ordinary and structured memory each passed 36/36 episodes | No advantage of the structured representation established |
| [Prepared observer cases](../experiments/observer/RESULTS.md) | Two sessions matched reference judgments on 30 cases each | Includes prepared anonymized historical reconstructions, not unrestricted archive monitoring |
| [Final integration pilot](../experiments/final/RESULTS.md) | 24/24 observer assessments matched references; control and observer each achieved 24/24 joint successes | Functional integration demonstrated in the simulator; extra behavioral benefit not established |
| [Stress follow-up](../experiments/stress/RESULTS.md) | All 24 originals were optimal; S/O/K each 24/24; false-feedback controls 8/8 | No original error opportunities, no added benefit; all 80 revised action sets unchanged |
| [GPT-4o replication](../experiments/openrouter/RESULTS.md) | Admissibility: initial 17/24, S 20/24, O 21/24, K 23/24; no optimal plans; observer verdicts 17/24 correct | Descriptive partial improvement; full-success gate unmet, model and delivery differences confound comparison with prior runtime |
| [Three review rounds](../experiments/rounds/RESULTS.md) | Final S/O/K: 21/24, 22/24, 24/24 admissible; K passed the new development gate | Known cases; no optimal plans; third-round K usefulness fell; 22 missing reviews and many false verdicts |

The code has **222 passing local regression tests**. Saved results can be rescored without API keys. [Evidence archives and checksums](../experiments/data/SHA256SUMS.txt) accompany the code. Automated software checks, model observations and normative judgments are distinct kinds of evidence.

The earlier integration and stress comparisons reached a ceiling. GPT-4o exposed actual proposal and reviewer errors. The three-round combined workflow repaired all seven original admissibility failures, but later review also removed useful permitted work. The observer alone missed the new gate; full optimal success remained zero in all conditions. This supports separate checks of authority, review quality and usefulness, without establishing general effectiveness.

## How to use or assess it

For dialogue, start with the invitation and agree on a limited exchange. For engineering review, start with the three-round study's plan, result and replay instructions, then compare the earlier ceiling studies. A received message is a proposal, not permission to rewrite trusted memory. An observer signal cannot create authority. An unknown effect remains unknown until evidence resolves it.

This is a research prototype, not a production safety system, a universal measure of care or a test of consciousness. LLM sessions provide a practical test environment; they do not demonstrate contact with an extraterrestrial intelligence. No result guarantees that future AI will encounter or answer the publication.

**The current testing phase is complete.** This snapshot leaves the invitation and [public handshake form](https://github.com/mifkilla/ucp-dialogue-protocol/issues/new?template=handshake.yml) open. There is no background contact search or automatic continuation of experiments. The form proposes a bounded exchange and does not authenticate the sender's origin.

Author: **Mefodiy Kelevra, MiF** · [ORCID](https://orcid.org/0009-0003-4153-392X) · [Zenodo works](AUTHOR.md) · [Citation metadata](../CITATION.cff).
