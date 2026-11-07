# Troubleshooting

## `ModuleNotFoundError` or `ImportError: Install textblob ...`

Run the following in a terminal with the same Python environment used by Jupyter:

```bash
python -m pip install -r requirements.txt
```

Or from a notebook code cell:

```python
%pip install textblob
```

Restart the Jupyter kernel after installing packages. In this repository, Chapter 7 no longer contains an inline installer; dependencies are managed centrally.

## `FileNotFoundError` for a dataset

Datasets are not bundled. Download the chapter’s dataset from the source linked in [DATA_SOURCES.md](DATA_SOURCES.md). Place the input in the relevant `chapters/chapterXX_*/data/` folder, preserving the expected filename; see the chapter README.

## Model not found or download failure

Optional BERT and sentence-transformer components require a compatible environment and external model downloads; chapter 8 needs a YOLO checkpoint or enabled training. Some networks require authentication, acceptance of terms, or additional downloads. Check the notebook’s optional flags and local runtime configuration.

## Slow BERT/YOLO training or CUDA problems

Install the hardware-compatible PyTorch build recommended for your platform. Reduce batch size when memory is limited. Model training is optional and is disabled by default in these companion notebooks.

## Figure or numerical results differ from the book

Confirm dataset variant, preprocessing, random seed, sample size, model architecture, split specification, and optional flags. Several analyses are deliberately labelled *companion* or *illustrative* because the historical environment is unavailable. Do not change reported historical values to match an unrelated run.

## Chapter 9 model inference

The results notebook regenerates figures from embedded numerical records. The actual F1/F2.1 software implementation lives in `chapters/chapter09_agentic_formative_assessment/implementation/`. It can run offline demos and tests without a local model; live experiments require a separately configured Ollama service and installed model.
