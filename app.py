import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Auto Film Maker API")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class FileContent(BaseModel):
    content: str

@app.get("/")
def index():
    """Serve the main web layout."""
    layout_path = os.path.join(WORK_DIR, "web_layout.html")
    if not os.path.exists(layout_path):
        return HTMLResponse("<h1>web_layout.html not found</h1>", status_code=404)
    with open(layout_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

def build_tree(dir_path):
    """Recursively build a directory tree."""
    tree = []
    try:
        entries = sorted(os.scandir(dir_path), key=lambda e: (not e.is_dir(), e.name))
        for entry in entries:
            # Ignore hidden files, virtual environments, and caches
            if entry.name.startswith('.') or entry.name in ['__pycache__', 'venv', 'node_modules']:
                continue
            
            item = {
                "name": entry.name,
                "path": os.path.relpath(entry.path, WORK_DIR).replace("\\", "/"),
                "is_dir": entry.is_dir(),
            }
            if entry.is_dir():
                item["children"] = build_tree(entry.path)
            tree.append(item)
    except Exception as e:
        pass # Handle permission denied or other errors gracefully
    return tree

@app.get("/api/fs/tree")
def get_file_tree():
    """Return the file tree of the workspace."""
    return build_tree(WORK_DIR)

@app.get("/api/fs/file")
def get_file_content(path: str):
    """Read file content."""
    full_path = os.path.abspath(os.path.join(WORK_DIR, path))
    # Security check: ensure path is within WORK_DIR
    if not full_path.startswith(WORK_DIR):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Cannot read binary file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/fs/file")
def save_file_content(path: str, data: FileContent):
    """Save file content."""
    full_path = os.path.abspath(os.path.join(WORK_DIR, path))
    if not full_path.startswith(WORK_DIR):
        raise HTTPException(status_code=403, detail="Access denied")
        
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(data.content)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)