import json
import os
from datetime import datetime, timezone
from github import Github

def push_notebook(notebook: dict, slug: str) -> dict[str, str]:
    token = os.getenv("GITHUB_TOKEN")
    username = os.getenv("GITHUB_USERNAME", "kareem-2727")
    repo_name = os.getenv("GITHUB_REPO", "ideaforge")
    branch = os.getenv("GITHUB_BRANCH", "main")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not configured.")
    repo = Github(token).get_repo(f"{username}/{repo_name}")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = f"notebooks/{timestamp}_{slug}.ipynb"
    content = json.dumps(notebook, ensure_ascii=False, indent=2)
    result = repo.create_file(path, f"Add generated notebook: {slug}", content, branch=branch)
    return {"path": path, "url": result["content"].html_url, "download_url": result["content"].download_url}
