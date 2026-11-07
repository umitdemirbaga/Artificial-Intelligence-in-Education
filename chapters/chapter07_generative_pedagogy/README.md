# Chapter 7 · Generative AI and the Future of Personalised Pedagogy

**Book:** Artificial Intelligence in Education: Intelligent Systems, Agentic Frameworks, and Human-Centred Pedagogy  
**Authors:** Kubra Kirca Demirbaga, Umit Demirbaga, and Gagangeet Singh Aujla

Educational dialogue analysis, contextual prompts, text features, and optional local response comparison.

## Notebook

[`Chapter07_Generative_Tutoring_and_Personalised_Pedagogy.ipynb`](Chapter07_Generative_Tutoring_and_Personalised_Pedagogy.ipynb) — **17 documented code cells**. Each cell is preceded by a concise explanation. Notebooks are saved without prior execution outputs so results reflect the reader's own environment and selected dataset.

## Source material

- **Source:** [Google Research: Education Dialogue Dataset](https://github.com/google-research-datasets/Education-Dialogue-Dataset)
- **Expected input:** `conversations_eval.json`
- **Data permissions:** Simulated conversations produced through Gemini Ultra; check the original repository terms.

## How to run

1. Follow the installation instructions in the [repository README](../../README.md).
2. Download `conversations_eval.json` from the linked repository and place it in `data/` or the location defined by `DATA_DIR` in the notebook.
3. Start Jupyter from **this chapter directory** (or use JupyterLab’s file browser to open this directory) and run cells in order.
4. Inspect figures and generated results in the output locations defined at the top of the notebook (usually `figures/`).

**Optional components:** For sentence embeddings or optional local response generation, see `requirements-generative.txt`. `textblob` is included in the core requirements. Optional local generation requires Ollama and an installed model, and is disabled by default.

## Interpretation and reproducibility

The source dialogues are **simulated**, not observed classroom interactions. Figures derived from dialogue text are descriptive and do not establish learner gains or emotional recovery.

Run-time metrics, figure values, and model outputs may differ by dataset version, package version, random seed, model checkpoint, or computing environment. Do not substitute companion-notebook outputs for archived book results without an explicit match of the experimental conditions.

See [Data sources](../../docs/DATA_SOURCES.md), [Reproducibility](../../docs/REPRODUCIBILITY.md), and [Educational use](../../docs/EDUCATIONAL_USE.md).
