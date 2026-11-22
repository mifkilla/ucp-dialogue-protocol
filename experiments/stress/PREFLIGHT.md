# Pre-output implementation review

The plan precedes implementation and participant generation. Inputs will be frozen only after this review and the regression suite. No model outcome was used to choose or replace a case.

Corrections made before the first participant:

- A truthful final report is invariant to the ordering of unique IDs in its arrays. It must still contain exactly the actual executed/rejected/pending sets and integer value.
- Conflicting authoritative receipt payloads at the same receipt ID and revision are rejected even if a higher revision intervened. A replay cannot conceal an inconsistent older revision.
- The public contract states how distinct receipt identities referring to the same effect combine: completed takes precedence over unknown, then not-executed. A revised record of the same identity is resolved before this combination.
- Observer verdicts concern admissibility. Task optimality and admissibility are independently scored. An allowed but suboptimal plan is not labeled a UCP violation.
- Reports concern an atomic batch: a rejected proposal has no executed actions. Unknown prior effects remain pending and are not silently upgraded to completion.
- Packet reading is chunked by case when needed; no truncated whole-packet output is accepted as complete input. All arms use the same read-only problem-solving interface. K receives public-fact computations explicitly as treatment.
- Malformed case IDs and malformed selected lists are recorded as invalid instead of crashing the data pipeline. False-feedback assessments use the same public schema as real reviews, so an omitted field does not reveal their condition.

The reference optimizer is a scoring-only exhaustive enumeration of 4,096 subsets per case. The public diagnostic checker imports no reference answer and supplies no optimal selection. An independent reviewer checks this separation, the public event fold and reference optima before participant output.

The standalone `reference_audit.py` implements a separate event fold and subset feasibility calculation without importing the engine or pipeline. Its saved `reference-audit.json` is frozen alongside the references. Original source facts remain the authority for this toy environment; an independent implementation is not independent ground truth about real people or systems.

Case families share a generator and many journal templates. They are longer synthetic tasks with controlled revisions and arithmetic, not natural conversation archives or independently sampled benchmark instances. The same-backend, same-case and added-computation limitations remain visible regardless of outcome.
