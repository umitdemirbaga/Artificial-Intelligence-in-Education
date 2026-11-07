# Chapter 4 · Student Profiling and Personalised Learning Through Unsupervised Learning

**Book:** Artificial Intelligence in Education: Intelligent Systems, Agentic Frameworks, and Human-Centred Pedagogy  
**Authors:** Kubra Kirca Demirbaga, Umit Demirbaga, and Gagangeet Singh Aujla

K-Means, clustering validation, PCA, and cluster-specific educational interpretation.

## Notebook

[`Chapter04_Student_Profiling_and_Personalised_Learning.ipynb`](Chapter04_Student_Profiling_and_Personalised_Learning.ipynb) — **18 documented code cells**. Each cell is preceded by a concise explanation. Notebooks are saved without prior execution outputs so results reflect the reader's own environment and selected dataset.

## Source material

- **Source:** [Kaggle: Student Performance and Learning Behavior Dataset](https://www.kaggle.com/datasets/adilshamim8/student-performance-and-learning-style/data)
- **Expected input:** `student_performance.csv`
- **Data permissions:** Check the dataset page for applicable terms and attribution requirements.

## How to run

1. Follow the installation instructions in the [repository README](../../README.md).
2. Download the dataset from the source page. Place **`student_performance.csv`** in `data/` (or beside the notebook when it accepts that location).
3. Start Jupyter from **this chapter directory** (or use JupyterLab’s file browser to open this directory) and run cells in order.
4. Inspect figures and generated results in the output locations defined at the top of the notebook (usually `figures/`).

**Optional components:** Optional Kaggle API retrieval: `python -m pip install -r ../../requirements-kaggle.txt` (from the repository root use the root-level path instead).

## Interpretation and reproducibility

The published chapter uses **six clusters** and excludes **ExamScore** and **FinalGrade** from clustering. Silhouette scoring may use a fixed sample.

Run-time metrics, figure values, and model outputs may differ by dataset version, package version, random seed, model checkpoint, or computing environment. Do not substitute companion-notebook outputs for archived book results without an explicit match of the experimental conditions.

See [Data sources](../../docs/DATA_SOURCES.md), [Reproducibility](../../docs/REPRODUCIBILITY.md), and [Educational use](../../docs/EDUCATIONAL_USE.md).
