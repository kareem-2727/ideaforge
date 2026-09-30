# IdeaForge

IdeaForge converts a text idea (and optionally a character/persona image) into a valid executable Jupyter Notebook **without using any AI model or AI API**.

The generator is deterministic and local. GitHub is used only to store the generated notebook.

## Stack
- React + Vite + Tailwind CSS
- FastAPI
- nbformat
- PyGithub

## Cost
Notebook generation itself does not consume AI credits. A GitHub token is required by the backend to publish files to GitHub.
