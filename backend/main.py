import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from github_pusher import push_notebook
from notebook_generator import generate_notebook

load_dotenv(Path(__file__).with_name(".env"))
app = FastAPI(title="IdeaForge API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
MAX_IMAGE_BYTES = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp"}

@app.get("/health")
def health(): return {"ok": True}

@app.post("/api/generate")
async def generate(idea: str = Form(...), image: UploadFile = File(...)):
    idea = idea.strip()
    if not idea: raise HTTPException(400, "Please describe your idea.")
    if image.content_type not in ALLOWED_TYPES: raise HTTPException(400, "Use PNG, JPEG, or WebP.")
    data = await image.read()
    if len(data) > MAX_IMAGE_BYTES: raise HTTPException(413, "Image must be 10 MB or smaller.")
    try:
        notebook, slug = generate_notebook(idea, data, image.content_type)
        github = push_notebook(notebook, slug)
        return {"filename": f"{slug}.ipynb", "preview": notebook.get("cells", [])[:3], "github": github, "notebook": notebook}
    except Exception as exc:
        raise HTTPException(500, f"Generation failed: {exc}") from exc

@app.post("/api/download")
async def download(payload: dict):
    import json
    notebook = payload.get("notebook")
    if not isinstance(notebook, dict): raise HTTPException(400, "Invalid notebook.")
    return Response(content=json.dumps(notebook, ensure_ascii=False, indent=2), media_type="application/x-ipynb+json", headers={"Content-Disposition": 'attachment; filename="ideaforge.ipynb"'})
