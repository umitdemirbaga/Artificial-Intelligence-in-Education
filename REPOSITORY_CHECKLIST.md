# Before publishing on GitHub

- [ ] Confirm the repository name and description on GitHub; no repository URL has been assigned in the documentation.
- [ ] Confirm the **MIT license** is the intended license for original companion code. The Chapter 9 implementation retains its original license file.
- [ ] Review the listed author names, affiliation text (if added later), and rights to redistribute any contributed code.
- [ ] Confirm no private datasets, student records, tokens, model files, or restricted expert annotations were added to the folders.
- [ ] Verify the source datasets' reuse conditions, especially Kaggle and Roboflow.
- [ ] If an ISBN, DOI, or publication date is assigned, update `CITATION.cff` and the README.
- [ ] Run `python scripts/validate_repository.py` and the Chapter 9 offline tests.
- [ ] Do not describe Chapter 6 text labels as clinical diagnoses or Chapter 7 simulated dialogues as real classroom observations.
- [ ] Resolve or explicitly disclose the Chapter 8 dataset/class mismatch before claiming to reproduce the book results.
- [ ] Optionally enable GitHub Actions in repository settings to run the included validation workflow.

## Upload sequence

1. Extract the archive locally.
2. In GitHub, create an empty repository (for example, `AI-in-Education-Companion`).
3. Upload **the contents of the extracted repository folder**, not the ZIP as a single file.
4. Commit changes and verify that GitHub renders the README and Jupyter notebooks correctly.
