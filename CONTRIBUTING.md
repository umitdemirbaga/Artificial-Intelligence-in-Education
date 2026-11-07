# Contributing

This repository is a companion to an academic book. Contributions should preserve the distinction between code demonstrations, independently verified research findings, and educational interpretation.

- Open an issue describing the affected chapter, software version, expected behaviour and reproducible steps.
- Do not upload student records, psychological health texts linked to individuals, API keys, private assessment files, third-party datasets or large model checkpoints.
- Keep every notebook code cell preceded by a short, informative English explanation.
- Explain any change that affects model settings, variables, dataset versions, seeds, statistical assumptions, or book figures.
- If an analysis is only illustrative, label it clearly; do not report simulated or hard-coded values as experimental measurements.
- Verify notebook JSON integrity using `python scripts/validate_repository.py`.
- Test code changes with the relevant documented dataset or a clearly described non-sensitive fixture. Never claim a synthetic smoke test is a replication of the book’s numbers.

Contributed code is expected to be compatible with the repository license. Cite and respect any third-party intellectual property separately.
