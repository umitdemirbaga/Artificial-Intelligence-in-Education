# Independent evaluation: scope and interpretation

The frozen independent comparison used 76 disjoint held-out problem inputs for each of the F1 and F2.1 configurations. Predictions were recorded before reference-answer evaluation. The restricted inputs, predictions, and private reviewer mapping are intentionally excluded from this public repository.

## Operational outcomes

| Metric | F1 | F2.1 |
| --- | ---: | ---: |
| Paired test inputs | 76 | 76 |
| Generated diagnoses | 70 | 76 |
| Generated feedback drafts | 70 | 76 |
| Saved local-model calls | 145 | 152 |
| Mean elapsed seconds per case | 91.42 | 104.338 |
| Automatic feedback released to learners | 0 | 0 |

The coverage difference comprises six discordant problem pairs, all favoring F2.1. The exact two-sided McNemar p-value for **output coverage alone** is 0.03125. The inference applies only to output coverage, not mathematical correctness or pedagogical quality.

## Independent expert review

A predefined 30-problem review sample contained 60 possible system responses, 58 of which had usable drafts. One independent expert evaluated these 58 outputs using four 0–2 dimensions: diagnosis, mathematics, evidence, and pedagogy. The expert flagged **26/58 (44.8%)** outputs as having a critical error. The overall dimension averages reported in the review were 1.00, 0.84, 1.10, and 0.72, respectively.

A single independent expert is not sufficient to estimate inter-rater reliability for this held-out review. The questions also contained several ambiguous or imperfect items; this should be accounted for in interpretation. Earlier development-phase multi-rater results should not be presented as multi-rater evidence for the independent held-out review.

**Conclusion:** F2.1 produced outputs more often but this did not establish superior mathematical accuracy. The high observed critical-error rate argues against unattended formative feedback. These outcomes describe a bounded, teacher-supervised research prototype, not a validated classroom intervention.
