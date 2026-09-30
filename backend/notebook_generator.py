import base64
import json
import os
import re
from typing import Any

import nbformat
from anthropic import Anthropic

SYSTEM_PROMPT = """You are a Jupyter Notebook architect. Given an idea and a character image, generate a complete, executable Jupyter Notebook in valid JSON (.ipynb format) that:
- Has a title cell with the idea name
- Includes the character image displayed in a markdown cell
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

def generate_notebook(idea: str, image_bytes: bytes, image_mime: str) -> tuple[dict[str, Any], str]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured.")
    client = Anthropic(api_key=api_key)
    image_data = base64.b64encode(image_bytes).decode("ascii")
    response = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role":"user","content":[{"type":"text","text":f"IDEA:\\n{idea}"},{"type":"image","source":{"type":"base64","media_type":image_mime,"data":image_data}}]}],
    )
    raw = "".join(block.text for block in response.content if getattr(block, "type", None) == "text")
    notebook = nbformat.from_dict(extract_json(raw))
    nbformat.validate(notebook)
    return notebook, slugify(idea)
