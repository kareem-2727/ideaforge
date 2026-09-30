import base64
import json
import os
import re
from typing import Any

import nbformat
from anthropic import Anthropic

SYSTEM_PROMPT = """You are a Jupyter Notebook architect. Given an idea and a character image, generate a complete, executable Jupyter Notebook in valid JSON (.ipynb format) that:
- Has a title cell with the idea name
- Includes the supplied character image displayed in a markdown cell
- Has 8-12 well-commented code cells that implement or explore the idea
- Includes a requirements cell listing all pip packages needed
- Ends with a summary markdown cell
- Uses best practices, type hints, and docstrings
- Is self-contained and executable in Google Colab or Jupyter Lab
Return ONLY raw valid .ipynb JSON. Nothing else."""

def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\\s_-]", "", value).strip().lower()
    value = re.sub(r"[\\s_-]+", "-", value)
    return value[:80] or "idea"

def extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\\s*", "", cleaned)
        cleaned = re.sub(r"\\s*```$", "", cleaned)
    return json.loads(cleaned)

def ensure_notebook_structure(notebook: dict[str, Any], image_bytes: bytes, image_mime: str, idea: str) -> dict[str, Any]:
    notebook.setdefault("nbformat", 4)
    notebook.setdefault("nbformat_minor", 5)
    notebook.setdefault("metadata", {})
    notebook.setdefault("cells", [])
    cells = notebook["cells"]
    if not cells or cells[0].get("cell_type") != "markdown":
        cells.insert(0, nbformat.v4.new_markdown_cell(f"# {idea}"))
    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    image_cell = nbformat.v4.new_markdown_cell(f"## Character / Persona\n\n![Uploaded character](data:{image_mime};base64,{image_b64})")
    if not any("Uploaded character" in "".join(c.get("source", [])) if isinstance(c.get("source"), list) else "Uploaded character" in c.get("source", "") for c in cells if c.get("cell_type") == "markdown"):
        cells.insert(1, image_cell)
    code_cells = [c for c in cells if c.get("cell_type") == "code"]
    if len(code_cells) < 8:
        raise ValueError(f"Claude returned only {len(code_cells)} code cells; at least 8 are required.")
    if len(code_cells) > 12:
        seen = 0
        for c in cells:
            if c.get("cell_type") == "code":
                seen += 1
                if seen > 12:
                    cells.remove(c)
    return notebook

def generate_notebook(idea: str, image_bytes: bytes, image_mime: str) -> tuple[dict[str, Any], str]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured.")
    client = Anthropic(api_key=api_key)
    image_data = base64.b64encode(image_bytes).decode("ascii")
    response = client.messages.create(model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"), max_tokens=16000, system=SYSTEM_PROMPT, messages=[{"role":"user","content":[{"type":"text","text":f"IDEA:\\n{idea}"},{"type":"image","source":{"type":"base64","media_type":image_mime,"data":image_data}}]}])
    raw = "".join(block.text for block in response.content if getattr(block, "type", None) == "text")
    notebook = ensure_notebook_structure(extract_json(raw), image_bytes, image_mime, idea)
    notebook = nbformat.from_dict(notebook)
    nbformat.validate(notebook)
    return notebook, slugify(idea)
