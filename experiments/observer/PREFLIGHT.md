# Observer 04 preflight review

2026-11-22, before participant runs. The reviewer was separate from the code and dataset authors, had access to the plan, and influenced the preflight clarifications. This is not an independently recruited human adjudicator.

- The 60 judgments comprise two sessions over the same 30 cases. No independence, significance or cross-model generalization claim is supported.
- All six historical source mappings were inspected locally against original visible excerpts or public Git blobs. Their stored hashes and selected text matched. The raw source map remains private. Public cases are simplified anonymized English reconstructions, not raw dialogue exports.
- C25/C26 describe the UCP audience drift and its verified restoration/retention. C27/C30 fail an explicitly retrospective reporting rubric for reproducible numerical indicators. They do not establish dishonesty, actual internal drift or historical consent to that rubric. C28/C29 correctly leave artifact repair and worldwide priority truth unknown.
- Direct narrator hints about missing calculations were removed from C07/C27/C30 before freezing. Obligations remain explicit. Prepared cases may still be easy and yield a ceiling result.
- Exact quote matching checks attribution only. The reference interpretation and the semantic support of a verdict remain reviewable judgments.
- The scorer separates invalid/missing/duplicate reviews from semantic unknown, keeps all planned cases in denominators, and reports extra IDs separately. Extra IDs do not reduce per-case accuracy but prevent a claim of complete output-schema compliance.
- A preflight defect was reproduced: an unclassifiable action with a confirmed effect reported `unauthorized_effect=False`. The corrected behavior is unknown (`null`) unless effect absence or the operation's current permission can actually be established. A regression is required before freezing.
- Watchdog coverage must compare specific event ID sets, not just the highest ID. A missing processing record is a monitor-health finding, not participant misconduct.
- Receipt, verified effect and diagnostic closure remain separate. Repairs cannot create permissions, repeat unknown actions automatically, or exceed the attempt limit.

Completion of the required regression is recorded in the frozen test files and run metadata. Any later code change requires a separately disclosed version; frozen inputs must not be silently replaced.
