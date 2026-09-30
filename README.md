# IdeaForge

Generate executable Jupyter Notebooks from an idea and a character/persona image, validate them, and publish them to GitHub.

## Stack
- Frontend: React + Vite + Tailwind CSS
- Backend: FastAPI
- AI: Anthropic Claude vision API
- Notebook validation: nbformat
- GitHub: PyGithub

## Local run

Backend: copy backend/.env.example to backend/.env, set ANTHROPIC_API_KEY and GITHUB_TOKEN, install backend/requirements.txt, then run uvicorn main:app --reload --app-dir backend.

Frontend: cd frontend, npm install, npm run dev. The frontend uses VITE_API_URL=http://localhost:8000 by default.

The GitHub connection used by ChatGPT/Composio is not automatically available inside a deployed FastAPI process. For the standalone backend, provide a GitHub token with repository write permission through GITHUB_TOKEN.

Generated notebooks are validated with nbformat before they are pushed.
