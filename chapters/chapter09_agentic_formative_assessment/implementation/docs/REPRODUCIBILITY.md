# Reproducibility

## Offline verification

1. Install Python 3.10 or newer.
2. Open the repository root in a terminal.
3. Run `python -m unittest discover -s . -t . -p "test_*.py" -v`.
4. Open `notebooks/Formative_Assessment.ipynb` and run all cells without enabling the optional local inference.

No model service, network connection, or private dataset is required for these steps.

## Live local example

Start Ollama with an installed `qwen3:4b-instruct` model. Change the notebook's `RUN_LOCAL_EXAMPLE` flag to `True` and run the optional inference cell. A live run is a demonstration on an original synthetic example, **not** a rerun of the held-out independent experiment.

For any new research evaluation, predeclare the dataset split, prompts, model configuration, performance measures, and human review protocol. Keep reference answers out of inference prompts; preserve input and code fingerprints and the complete output records. Use new experiment directories when the configuration changes.

The independent evaluation's restricted raw material is not distributed. The released source can reproduce the pipeline and software tests but cannot reproduce those exact results without access to the restricted inputs and recorded model environment.
