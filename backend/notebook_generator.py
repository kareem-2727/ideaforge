import re
from typing import Any
import nbformat

def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9\\s_-]", "", value).strip().lower()
    value = re.sub(r"[\\s_-]+", "-", value)
    return value[:80] or "idea"

def generate_notebook(idea: str, image_bytes: bytes | None = None, image_mime: str | None = None) -> tuple[dict[str, Any], str]:
    """Create a self-contained notebook locally. No AI or external model is used."""
    title = idea.strip() or "My Idea"
    cells = [
        nbformat.v4.new_markdown_cell(f"# {title}\n\nGenerated automatically by IdeaForge from your idea."),
        nbformat.v4.new_markdown_cell("## Idea\n\n" + title),
        nbformat.v4.new_markdown_cell("## Requirements\n\nThis notebook uses only Python's standard library unless you add packages to the list below.\n\n```text\n# Add project-specific packages here\n```"),
        nbformat.v4.new_code_cell("# Configuration\nfrom pathlib import Path\nfrom typing import Any\n\nPROJECT_NAME = " + repr(title) + "\nprint(f'Project: {PROJECT_NAME}')"),
        nbformat.v4.new_code_cell("# Input data placeholder\ndata: list[Any] = []\n\n# Add or load the data required by your idea here.\nprint('Data items:', len(data))"),
        nbformat.v4.new_code_cell("# Core implementation\ndef run_idea() -> dict[str, Any]:\n    \"\"\"Main execution function generated from the supplied idea.\"\"\"\n    return {\"idea\": PROJECT_NAME, \"status\": \"ready for implementation\"}\n\nresult = run_idea()\nprint(result)"),
        nbformat.v4.new_code_cell("# Validation\nassert isinstance(result, dict)\nassert result.get('idea') == PROJECT_NAME\nprint('Basic validation passed.')"),
        nbformat.v4.new_code_cell("# Example execution\nexample_result = run_idea()\nprint(example_result)"),
        nbformat.v4.new_code_cell("# Export\noutput = Path('ideaforge_output.txt')\noutput.write_text(str(result), encoding='utf-8')\nprint(f'Saved: {output.resolve()}')"),
        nbformat.v4.new_code_cell("# Extension point\n# Add the project-specific algorithms, UI, data processing, or integrations here.\nprint('Notebook structure is ready.')"),
        nbformat.v4.new_markdown_cell("## Summary\n\nThe notebook was generated locally from the supplied idea. No AI model or AI API is required to create this file.\n\n**Next step:** customize the implementation cells for the exact project requirements."),
    ]
    if image_bytes and image_mime:
        import base64
        encoded = base64.b64encode(image_bytes).decode("ascii")
        cells.insert(1, nbformat.v4.new_markdown_cell(f"## Character / Persona\n\n![Uploaded character](data:{image_mime};base64,{encoded})"))
    notebook = nbformat.v4.new_notebook(cells=cells, metadata={"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python"}})
    nbformat.validate(notebook)
    return notebook, slugify(title)
