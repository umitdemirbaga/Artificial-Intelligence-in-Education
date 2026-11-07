"""Validate companion repository structure and notebook source without executing cells."""
from __future__ import annotations
import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
notebooks = sorted((ROOT / "chapters").glob("chapter*/*.ipynb"))
errors = []
if len(notebooks) != 8:
    errors.append(f"Expected eight primary notebooks, found {len(notebooks)}")
count_total = 0
for p in notebooks:
    try:
        nb = json.loads(p.read_text(encoding="utf-8"))
        assert nb["nbformat"] == 4
        cells = nb["cells"]
        count = 0
        for k, cell in enumerate(cells):
            if cell["cell_type"] != "code":
                continue
            count += 1
            source = "".join(cell["source"])
            ast.parse(source, filename=str(p))
            if cell.get("execution_count") is not None or cell.get("outputs"):
                errors.append(f"Cached output in {p.name} at cell {k}")
            if k == 0 or cells[k - 1]["cell_type"] != "markdown":
                errors.append(f"Missing preceding explanation at {p.name} cell {k}")
        count_total += count
        print(f"OK  {p.parent.name}: {count} documented code cells")
    except (OSError, KeyError, ValueError, SyntaxError, AssertionError) as exc:
        errors.append(f"{p}: {exc}")
print(f"Primary notebooks: {len(notebooks)} | Code cells: {count_total}")
if errors:
    print("\nValidation errors:", file=sys.stderr)
    print("\n".join("- " + x for x in errors), file=sys.stderr)
    sys.exit(1)
print("Repository structural validation passed.")
