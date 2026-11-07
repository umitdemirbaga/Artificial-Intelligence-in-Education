# Reproducibility and verification

## Three different claims

**Software execution:** the notebook cells run under a stated environment.  
**Analysis reproduction:** the same input data and modelling configuration yield corresponding derived figures and metrics.  
**Study replication:** a new, independently executed assessment provides comparable evidence about educational performance.

These claims are not interchangeable. A passing notebook smoke test or a generated plot alone does not establish independent replication of the book's findings.

## Recommended record for each run

1. Exact dataset version or checksum and source citation.
2. Python and package versions, computing device and operating system.
3. Random seeds, data partitioning, preprocessing and model hyperparameters.
4. Whether optional training, external model calls or embeddings were enabled.
5. Observed scores together with uncertainty, held-out denominators and error cases.
6. Output files, changes to default settings, and known departures from the book.

## Chapter-specific reproducibility boundaries

| Chapter | Main issue |
|---|---|
| 2 | Mathematics versus Portuguese subset; G1/G2 availability and partitioning. |
| 3 | GRADE-derived risk definition, sample size, coded predictors and threshold choice. |
| 4 | Selected `k=6`, nine clustering predictors, silhouette sampling and dataset version. |
| 5 | BIC learning and probability estimates depend on discretisation and graph assumptions. |
| 6 | BERT training is optional and can be resource intensive; no clinical validation. |
| 7 | Source conversations are simulated; optional generative comparisons are new experiments. |
| 8 | Roboflow v3 classes differ from historical chapter labels; YOLO training is optional. |
| 9 | Operational tabulation is included; original held-out item content and review records are restricted. |

## Notebook outputs

Primary notebooks are distributed with code and documentation but without cached output cells. This is intentional: users should execute the notebooks with traceable inputs rather than mistake cached demonstration outputs for their own results. Figures and other generated files should remain outside version control unless a new version is explicitly archived and documented.

The `scripts/validate_repository.py` checker verifies notebook JSON and code syntax, but does not train models or download datasets. The Chapter 9 software unit tests verify deterministic functions and offline processing; they do not measure learning gains.
