# Architecture

The software is organized into two comparable assessment pipelines and a shared set of utilities.

| Component | Purpose |
| --- | --- |
| `chapter9_system` | F1 baseline, input contracts, bounded arithmetic evaluator, teacher-review routing, experiment recording, and CSV review utilities |
| `chapter9_f2` | Shared diagnosis and arithmetic risk inspections used by F2.1 |
| `chapter9_f21` | F2.1 structured message contracts, schema validation, diagnostic and feedback pipeline, and versioned experiment recording |
| `tests`, `tests_f2`, `tests_f21` | Automated regression coverage without model calls |
| `notebooks` | Main runnable walkthrough and an independent, self-contained source notebook |

## Processing sequence

1. Validate the question and learner work.
2. Request a tentative diagnosis from a local model (or use a synthetic fixture for offline testing).
3. Check basic source grounding and any proposed arithmetic expression.
4. Request a teacher-facing feedback draft.
5. Apply conservative risk flags and route the output to teacher review.
6. Record the input digest, system configuration, response, and processing metadata for audit.

**Boundary:** The arithmetic evaluator can validate a permitted expression numerically, but not whether that expression faithfully models the question. A valid computation is not proof of a valid diagnosis. Teacher approval is required for all learner-facing use.
