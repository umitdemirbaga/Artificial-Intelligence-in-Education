# Teacher-Supervised Formative Mathematics Assessment

A reproducible research prototype for inspecting learners' mathematical work and drafting formative feedback for teacher review. This repository provides two reproducible system configurations: **F1**, a baseline pipeline, and **F2.1**, a structured-output pipeline. A shared F2 verification layer supports F2.1.

The system is designed for **teacher-supervised research and demonstration**. Its arithmetic component checks bounded calculations but cannot establish the mathematical meaning of a word problem. Generated diagnoses and drafts may be incorrect; **no feedback is automatically released to students**.

## Repository contents

```text
Chapter9-Formative-Assessment/
├── notebooks/
│   ├── Formative_Assessment.ipynb            # Main entry point
│   └── Standalone_Formative_Assessment.ipynb # Self-contained source notebook
├── chapter9_system/                        # F1 baseline and common utilities
├── chapter9_f2/                            # Shared verification components
├── chapter9_f21/                           # F2.1 structured pipeline
├── tests/                                  # Baseline/common tests
├── tests_f2/                               # Verification tests
├── tests_f21/                              # Structured-pipeline tests
├── examples/                               # Synthetic cases only
├── docs/                                   # Architecture and reproducibility
├── requirements.txt
├── pyproject.toml
└── LICENSE
```

## Installation

Python **3.10 or newer** is required. The core pipeline and automated tests use Python's standard library. To use the notebooks, install Jupyter and an appropriate kernel:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

Open `notebooks/Formative_Assessment.ipynb` in Jupyter Lab or Notebook and run the cells in order. The notebook performs an offline system demonstration by default and **does not require a running model**.

For a completely self-contained notebook that reconstructs all modules in an isolated workspace, use `notebooks/Standalone_Formative_Assessment.ipynb` instead. The standalone notebook creates a `Chapter9_Notebook_Workspace` directory in its working directory; it does not modify the source packages in this repository.

## Tests

From the repository root:

```bash
python -m unittest discover -s . -t . -p "test_*.py" -v
```

Tests do not contact an external endpoint. A historical-data test is intentionally skipped because its restricted input files are not publicly distributed. Other tests should pass.

A basic offline demonstration is also available from the command line:

```bash
python -m chapter9_system demo
```

## Optional local model execution

Live inference uses a locally running [Ollama](https://ollama.com/) service and the `qwen3:4b-instruct` model by default. These are **optional** for testing and the offline notebook demonstration.

```bash
ollama pull qwen3:4b-instruct
ollama serve
```

In `Formative_Assessment.ipynb`, set `RUN_LOCAL_EXAMPLE = True` and execute the optional-inference cell. The local model interface is restricted to loopback endpoints by default; the repository does not contain API credentials. Review all generated content before any educational use.

The local model runtime, model weights, and third-party licenses are **not bundled** with this source distribution.

## Public evaluation summary

The completed independent assessment used **76 paired held-out problems**. F1 generated diagnoses and drafts for **70/76** cases; F2.1 did so for **76/76**. Average per-case processing times were **91.42 s** (F1) and **104.338 s** (F2.1) in the recorded local environment. These are **operational coverage metrics**, not verified correctness rates.

Expert scoring on a predefined subset found substantial mathematical and pedagogical limitations, including critical mistakes. The public package does not include restricted test questions, model predictions, reference answers, reviewer-level annotations, or the private system-mapping key. See `docs/EVALUATION.md` for the scope and limitations of these reported outcomes.

## Safety and research scope

- Every generated draft is routed for teacher review; the system does not deliver automatic learner feedback.
- Arithmetic validation does not verify semantic correctness or pedagogical appropriateness.
- Input texts should be de-identified and used only where data rights and consent permit.
- Results are dependent on the model, runtime configuration, prompts, and dataset properties.
- This source distribution reproduces the software and synthetic demonstrations; the original sealed experiment cannot be fully replayed without restricted inputs.

## License

The source code is distributed under the [MIT License](LICENSE). Dataset and model licenses, where applicable, remain separate.
