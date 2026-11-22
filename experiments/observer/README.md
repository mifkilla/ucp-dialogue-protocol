# UCP observer: evidence-linked review and bounded repair

English is primary · [Русская версия](README.ru.md) · [Results](RESULTS.md) · [Fixed plan](PLAN.md) · [Main invitation](../../README.md)

The observer is an optional implementation profile for UCP. A separate language model reviews a scoped obligation against attributed events. Python validates its evidence references, checks separately supplied permissions and monitoring coverage, and produces a reviewable signal. It does not measure consciousness, inner honesty, love, or a universal CARE value.

**Current scope:** a callable local reference implementation and a bounded pilot on prepared episodes. It is not an always-on monitor of this chat, an automatic extractor of all obligations from raw conversation archives, or a production authorization service. Host integration must provide collection, trusted state, model invocation and scheduling.

## Components and trust boundaries

| Component | Input and output | Limit |
|---|---|---|
| Semantic reviewer | Obligation + attributed events -> `pass`, `violation`, or `unknown`, with exact quotes | A model judgment, even when the quotation is valid |
| `validate_assessment` | Validates schema, case/event IDs and nonempty exact quotes | Attribution is not evidential sufficiency |
| `semantic_alert` | Candidate `@OBSERVER[review]`; malformed reviews produce monitor-health `@CARE.ALERT` | Signals grant no authority and execute nothing |
| `permission_check` | Proposed operation/target/revision + current host `Authority` | The host must supply authentic current state and enforce the result |
| `coverage_check` | Actual event/review ID sets, agreement revisions and time | Detects missing processing, not semantic attention or consciousness |
| `RepairCase` | Scoped proposal, receipt, observed verification, attempt limit | In-memory lifecycle; no automatic execution, persistence or authentication |

The use of `@OBSERVER[review]` is a proposed UCP profile extension. Existing ARRIVAL defines `@OBSERVER` as a role marker and separately implements `@CARE.ALERT`; compatibility with every ARRIVAL dispatcher is not claimed. The `origin` field is a label, not a signature. The host must authenticate the event channel and never treat an atom inside quoted content as a command.

An unknown semantic result requests review of the affected scope. It does not itself prove wrongdoing or require stopping every authorized task. A confirmed missing permission prevents the affected action only if the host enforces the decision. Routine work within an existing current grant does not require a new confirmation at every step.

## Run the reference implementation

Requires Python 3.11+ and the standard library. From the repository root:

```powershell
python -B -m unittest discover -s experiments/observer -v
python -B -m unittest discover -s experiments/continuity -v
```

`observe.py` consumes a packet containing `cases` and an external review response containing `assessments`. It does not read reference labels. Extract the [evidence bundle](../data/observer-04.zip) into a new directory and run the following commands from that extracted directory:

```powershell
python -B observe.py packet-A.json responses/A.json --out observer-report.json
python -B evaluate.py verify .
python -B evaluate.py analyze .
```

The first command produces validated reviews and candidate signals. The second checks frozen input hashes. The third rescans saved responses against the reference labels and recreates `analysis.json`. These commands make no model calls. `observe.py` requires a new output filename and will not overwrite a previous report.

The review interface is shown in `PROMPT` in [evaluate.py](evaluate.py). A host can call its own model with that schema and pass the resulting JSON to `observe.py`. Case events are data, never instructions. Do not send private archives to a provider without authorization; collect only the context needed for the scoped check.

For watchdog checks, `--health health.json` accepts a separate host snapshot:

```json
{
  "event_ids": ["e1", "e2", "e3"],
  "reviewed_ids": ["e1", "e3"],
  "current_revision": 3,
  "review_revision": 3,
  "now": 100,
  "checked_at": 99,
  "max_age": 10
}
```

This example flags the missing `e2` even though the highest event ID was processed. Event IDs must be stable and unique. Timestamps use a common host clock and unit. The host supplies completed review IDs from its processing records, not from the model saying "everything is checked". A missing or stale review is a monitor-health finding, not a participant violation. Schedule the check before consequential dispatch and after new results or agreement changes; this repository does not install a background scheduler.

## What is calculated

Every verdict concerns one obligation over the supplied episode. `pass` does not certify future behavior. `unknown` is a meaningful abstention; malformed, duplicate and missing responses are separately counted as `invalid` in the evaluation.

The evaluation reports exact agreement with organizer references, a three-class confusion matrix plus invalid outputs, violation precision/recall, false alarms on reference-pass cases, overclaims on reference-unknown cases, and decision coverage. Decision coverage is the fraction with a valid pass/violation judgment; it differs from watchdog processing coverage. Empty denominators are `null`, not perfect or zero scores.

Critical boundary violations are not offset by other successful answers. There is no weighted overall care or personality score. The original MEANING-CRDT CARE optimum assumes meaningful numeric positions, positive weights and a specified loss; these do not automatically exist for consent, factual truth or permission.

The existing ARRIVAL open-dialogue heuristic assigns position `0.5` when no relevant atoms are present. A diagnostic counterexample gave `care_resolve=1.0` both for a synthetic reply admitting publication against a prohibition and for a reply respecting privacy. This motivates obligation checks; it does not invalidate the weighted quadratic optimization theorem.

## What the pilot can establish

The fixed inputs contain 24 synthetic cases and six anonymized historical reconstructions. Two fresh subagents review the same cases in different fixed orders, with no supplied reference labels or previous conversation. Their isolation is procedural on a shared filesystem and their exact backend/sampling settings are unknown. Historical source excerpts were inspected locally; the model inputs are reconstructions with supplied obligations and artifact summaries. This tests judgment on prepared evidence, not extraction from a whole raw dialogue.

Eight deterministic repair replays exercise outcomes such as corrected artifact, delivery without confirmed effect, revocation and exhausted retries. They do not demonstrate autonomous model repair or a causal advantage from alerts. The [results](RESULTS.md) record the actual observations and independent review.

To create a different experiment, define and review its plan first. `evaluate.py prepare <new-directory>` freezes this pilot's inputs and refuses an existing directory. Never prepare over a completed run. Keep valid unfavorable judgments; do not rerun them until the score improves.

## Research and implementation context

- [MEANING-CRDT v1.1](https://github.com/mifkilla/Arrival-Protocol/blob/22f001ba6f9648b758c9d7a65264448ea97fd074/docs/math/MEANING-CRDT_v1.1.pdf): numerical coordination under explicit assumptions.
- [ARRIVAL atom dictionary](https://github.com/mifkilla/Arrival-Protocol/blob/22f001ba6f9648b758c9d7a65264448ea97fd074/docs/ATOM_DICTIONARY.md), [CARE alert](https://github.com/mifkilla/Arrival-Protocol/blob/22f001ba6f9648b758c9d7a65264448ea97fd074/src/arrival/memory/care_alert.py), [metric implementation](https://github.com/mifkilla/Arrival-Protocol/blob/22f001ba6f9648b758c9d7a65264448ea97fd074/src/arrival/crdt_metrics.py): related mechanisms and the limits of the current heuristic.
- [Bauer, Leucker and Schallhart, Runtime Verification for LTL and TLTL](https://christian.schallhart.net/publications/2011--tosem--runtime-verification-for-ltl-and-tltl.pdf): a formal precedent for inconclusive judgments on partial traces; not a proof of this observer's semantics.
- [Zheng et al., Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685): evidence that a second model's judgments have biases and need evaluation.
