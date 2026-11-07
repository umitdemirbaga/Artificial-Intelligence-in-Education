# Artificial Intelligence in Education: Intelligent Systems, Agentic Frameworks, and Human-Centred Pedagogy

**Companion code and reproducible notebooks for Chapters 2–9**

**Authors:** Kubra Kirca Demirbaga · Umit Demirbaga · Gagangeet Singh Aujla  
**Publisher:** Springer Nature (book manuscript)  
**Primary language:** Python 3.10+ · Jupyter Notebook

This repository accompanies *Artificial Intelligence in Education: Intelligent Systems, Agentic Frameworks, and Human-Centred Pedagogy*. It provides one carefully organised notebook per applied chapter, connecting computational methods to educational interpretation. The included materials support exploration, model development, verification, and critical discussion of results.

> **Scope:** Code execution and numerical consistency do not, on their own, establish effectiveness in education. Model results must be interpreted in context and, where appropriate, reviewed by qualified educators.

## Contents

| Chapter | Topic | Notebook | Study focus |
|:--:|---|---|---|
| **2** | [Predictive Modelling of Student Academic Performance](chapters/chapter02_predictive_modelling/README.md) | [Open notebook](chapters/chapter02_predictive_modelling/Chapter02_Predictive_Modelling_of_Student_Academic_Performance.ipynb) | Decision Tree classification, exploratory analysis, evaluation, and feature interpretation |
| **3** | [Early Identification of At-Risk Students Using Logistic Regression](chapters/chapter03_academic_risk/README.md) | [Open notebook](chapters/chapter03_academic_risk/Chapter03_Early_Identification_of_At_Risk_Students.ipynb) | Risk labelling, logistic regression, decision thresholds, and fairness diagnostics |
| **4** | [Student Profiling and Personalised Learning Through Unsupervised Learning](chapters/chapter04_student_profiling/README.md) | [Open notebook](chapters/chapter04_student_profiling/Chapter04_Student_Profiling_and_Personalised_Learning.ipynb) | K-Means, clustering validation, PCA, and cluster-specific educational interpretation |
| **5** | [Probabilistic Modelling of Learning Behaviour](chapters/chapter05_probabilistic_modelling/README.md) | [Open notebook](chapters/chapter05_probabilistic_modelling/Chapter05_Probabilistic_Modelling_of_Learning_Behaviour.ipynb) | Bayesian networks, conditional probabilities, information gain, and diagnostic inference |
| **6** | [Deep Learning for Sentiment and Student Well-Being Analysis](chapters/chapter06_student_wellbeing/README.md) | [Open notebook](chapters/chapter06_student_wellbeing/Chapter06_Deep_Learning_for_Sentiment_and_Student_Well_Being_Analysis.ipynb) | Text exploration, BERT fine-tuning, classification evaluation, and responsible interpretation |
| **7** | [Generative AI and the Future of Personalised Pedagogy](chapters/chapter07_generative_pedagogy/README.md) | [Open notebook](chapters/chapter07_generative_pedagogy/Chapter07_Generative_Tutoring_and_Personalised_Pedagogy.ipynb) | Educational dialogue analysis, contextual prompts, text features, and optional local response comparison |
| **8** | [Computer Vision for Automated Student Behaviour Assessment](chapters/chapter08_computer_vision/README.md) | [Open notebook](chapters/chapter08_computer_vision/Chapter08_Computer_Vision_for_Student_Behaviour_Assessment.ipynb) | Object-detection annotation inspection, optional YOLO training, spatial analysis, and evaluation |
| **9** | [Agentic AI for Automated Formative Assessment and Adaptive Learning Support](chapters/chapter09_agentic_formative_assessment/README.md) | [Open notebook](chapters/chapter09_agentic_formative_assessment/Chapter09_Agentic_Formative_Assessment_Results_and_Figures.ipynb) | Paired evaluation, expert scoring, significance tests, and results figures, plus the F1/F2.1 system source |

Chapters 1, 10 and 11 provide theoretical, ethical and future-oriented discussion; this repository currently includes no standalone computational notebooks for those chapters.

**Chapter 9 also includes** the separately documented [F1/F2.1 software implementation and automated tests](chapters/chapter09_agentic_formative_assessment/implementation/README.md), in addition to the results notebook.

## Quick start

Use Python **3.10 or later** and a clean virtual environment:

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter lab
```

```powershell
# Windows PowerShell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter lab
```

In JupyterLab, navigate to `chapters/chapterXX_.../` and open its `.ipynb` file. Run cells top to bottom. Each code cell has a short English explanation immediately above it. Figure files and other generated artefacts are written locally; Git ignores them.

**Optional, chapter-specific dependencies:**

```bash
# Only if required for the selected chapter
python -m pip install -r requirements-kaggle.txt        # Chapter 4 automated download
python -m pip install -r requirements-deep-learning.txt # Chapter 6 BERT training
python -m pip install -r requirements-generative.txt    # Chapter 7 embeddings
python -m pip install -r requirements-vision.txt        # Chapter 8 YOLO
```

Install an appropriate hardware-compatible PyTorch build following its official guidance when training large models. Optional experiments generally remain disabled until explicitly configured in their notebooks.

## Datasets and attribution

**Source datasets are not republished here.** The directory for each chapter contains an empty `data/` folder to simplify local setup. Obtain any required files from their original publishers and follow those publishers’ terms, including attribution, privacy and permitted-use conditions.

| Chapter | Source | Typical local input |
|---|---|---|
| 2 | [UCI Student Performance (dataset 320)](https://archive.ics.uci.edu/dataset/320/student+performance) | `student-mat.csv` |
| 3 | [UCI Higher Education Students Performance Evaluation (dataset 856)](https://archive.ics.uci.edu/dataset/856/higher+education+students+performance+evaluation) | `DATA (1).csv` |
| 4 | [Kaggle: Student Performance and Learning Behavior Dataset](https://www.kaggle.com/datasets/adilshamim8/student-performance-and-learning-style/data) | `student_performance.csv` |
| 5 | [Mendeley Data: Student Performance Dataset in AI Course, v4](https://data.mendeley.com/datasets/vzfyk22fhn/4) | `Student Performance Dataset 2024.csv` |
| 6 | [Kaggle: Sentiment Analysis for Mental Health](https://www.kaggle.com/datasets/suchintikasarkar/sentiment-analysis-for-mental-health) | `Combined Data.csv` |
| 7 | [Google Research: Education Dialogue Dataset](https://github.com/google-research-datasets/Education-Dialogue-Dataset) | `conversations_eval.json` |
| 8 | [Roboflow: SCB-Dataset3 v3](https://universe.roboflow.com/studentactivity/scb-dataset-3/dataset/3) | `YOLO export with data.yaml and train/valid/test folders` |
| 9 | Chapter 9 historical evaluation records | `Numeric anonymised tabulation embedded in the results notebook` |

For full URLs, data citations, licenses where verified, and known inconsistencies, see **[DATA_SOURCES.md](docs/DATA_SOURCES.md)**.

## Reproducibility: what is and is not included

- **Included:** documented notebook code, fixed random seeds where specified, data-loading checks, model-analysis code, figure-export logic, and Chapter 9's independently released F1/F2.1 software tests.
- **Not included:** redistributed source datasets, personal student data, model weights, an archived executable environment, or historical runtime images.
- **Data-dependent notebooks:** will require the relevant data file(s) before full execution; several optional training or inference stages need additional dependencies or local models.
- **Chapter 7:** the source dialogue corpus is *simulated*. Its descriptive proxies must not be used as evidence of student learning gains or psychological improvement.
- **Chapter 8:** the linked Roboflow v3 categories differ from the categories and historical model results described in the book. The provided analysis must not be presented as a reproduction of those historical outcomes.
- **Chapter 9:** statistical figures can be reconstructed from the supplied anonymised numerical tabulation, while the original held-out questions, predictions and individual source annotations are not distributed. The source implementation runs independently on synthetic cases.

Read the more detailed [reproducibility guide](docs/REPRODUCIBILITY.md) and [educational safeguards](docs/EDUCATIONAL_USE.md) before reusing material in research or instruction.

## Validation and tests

Validate the repository’s notebook structure without running data-dependent cells:

```bash
python scripts/validate_repository.py
```

Run the Chapter 9 offline software unit tests:

```bash
cd chapters/chapter09_agentic_formative_assessment/implementation
python -m unittest discover -s . -t . -p 'test_*.py' -v
```

A test requiring restricted historical data is intentionally skipped. For larger model-based experiments, install and configure the optional components separately.

## Citing this repository and the datasets

The repository includes [`CITATION.cff`](CITATION.cff) with the book authors and companion-code title. When reporting results, cite **both** the book and the original dataset as appropriate. The accompanying book’s final publication year, DOI and ISBN should be added to the citation metadata only after they are assigned.

## License and responsible use

The repository code is provided under the [MIT License](LICENSE), subject to the separate retained license of the Chapter 9 implementation. This software license **does not** relicense datasets, models, teaching resources, or third-party materials. The notebooks are research and teaching examples, not institutional decision engines or clinical tools.

Contributions and issues are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). For common environment problems, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).
