# Chapter 6 · Deep Learning for Sentiment and Student Well-Being Analysis

**Book:** Artificial Intelligence in Education: Intelligent Systems, Agentic Frameworks, and Human-Centred Pedagogy  
**Authors:** Kubra Kirca Demirbaga, Umit Demirbaga, and Gagangeet Singh Aujla

Text exploration, BERT fine-tuning, classification evaluation, and responsible interpretation.

## Notebook

[`Chapter06_Deep_Learning_for_Sentiment_and_Student_Well_Being_Analysis.ipynb`](Chapter06_Deep_Learning_for_Sentiment_and_Student_Well_Being_Analysis.ipynb) — **22 documented code cells**. Each cell is preceded by a concise explanation. Notebooks are saved without prior execution outputs so results reflect the reader's own environment and selected dataset.

## Source material

- **Source:** [Kaggle: Sentiment Analysis for Mental Health](https://www.kaggle.com/datasets/suchintikasarkar/sentiment-analysis-for-mental-health)
- **Expected input:** `Combined Data.csv`
- **Data permissions:** Check the dataset page for applicable terms and attribution requirements.

## How to run

1. Follow the installation instructions in the [repository README](../../README.md).
2. Download the dataset from the source page. Place **`Combined Data.csv`** in `data/` (or beside the notebook when it accepts that location).
3. Start Jupyter from **this chapter directory** (or use JupyterLab’s file browser to open this directory) and run cells in order.
4. Inspect figures and generated results in the output locations defined at the top of the notebook (usually `figures/`).

**Optional components:** To enable BERT tokenisation and/or training, install `requirements-deep-learning.txt` at the repository root and switch on `RUN_TOKEN_ANALYSIS` and/or `RUN_TRAINING`. A compatible PyTorch installation and adequate compute resources are required.

## Interpretation and reproducibility

The source dataset is not a verified student cohort. Psychological categories are labels for text classification, **not clinical diagnoses**. BERT training is disabled by default.

Run-time metrics, figure values, and model outputs may differ by dataset version, package version, random seed, model checkpoint, or computing environment. Do not substitute companion-notebook outputs for archived book results without an explicit match of the experimental conditions.

See [Data sources](../../docs/DATA_SOURCES.md), [Reproducibility](../../docs/REPRODUCIBILITY.md), and [Educational use](../../docs/EDUCATIONAL_USE.md).
