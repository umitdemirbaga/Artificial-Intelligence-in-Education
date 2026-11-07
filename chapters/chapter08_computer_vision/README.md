# Chapter 8 · Computer Vision for Automated Student Behaviour Assessment

**Book:** Artificial Intelligence in Education: Intelligent Systems, Agentic Frameworks, and Human-Centred Pedagogy  
**Authors:** Kubra Kirca Demirbaga, Umit Demirbaga, and Gagangeet Singh Aujla

Object-detection annotation inspection, optional YOLO training, spatial analysis, and evaluation.

## Notebook

[`Chapter08_Computer_Vision_for_Student_Behaviour_Assessment.ipynb`](Chapter08_Computer_Vision_for_Student_Behaviour_Assessment.ipynb) — **17 documented code cells**. Each cell is preceded by a concise explanation. Notebooks are saved without prior execution outputs so results reflect the reader's own environment and selected dataset.

## Source material

- **Source:** [Roboflow: SCB-Dataset3 v3](https://universe.roboflow.com/studentactivity/scb-dataset-3/dataset/3)
- **Expected input:** `YOLO export with data.yaml and train/valid/test folders`
- **Data permissions:** Check Roboflow dataset page for permitted use and required attribution.

## How to run

1. Follow the installation instructions in the [repository README](../../README.md).
2. Export Roboflow v3 in **YOLOv8 format** and set the notebook’s `DATA_ROOT` to the export location; preserve the `data.yaml` and original split folders.
3. Start Jupyter from **this chapter directory** (or use JupyterLab’s file browser to open this directory) and run cells in order.
4. Inspect figures and generated results in the output locations defined at the top of the notebook (usually `figures/`).

**Optional components:** For object detection training or checkpoint evaluation, install `requirements-vision.txt`; the notebook’s training switches remain disabled until explicitly enabled.

## Interpretation and reproducibility

**Dataset mismatch:** Roboflow v3 class labels do not match the chapter’s historical Doing Homework/Listening/Looking Around classes. This notebook does not reproduce the original book’s YOLO experiment. Training is disabled by default.

Run-time metrics, figure values, and model outputs may differ by dataset version, package version, random seed, model checkpoint, or computing environment. Do not substitute companion-notebook outputs for archived book results without an explicit match of the experimental conditions.

See [Data sources](../../docs/DATA_SOURCES.md), [Reproducibility](../../docs/REPRODUCIBILITY.md), and [Educational use](../../docs/EDUCATIONAL_USE.md).
