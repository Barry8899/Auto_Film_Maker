import os
import uuid
import json
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

# Mount the workspace directory to serve static files (like media)
app.mount("/files", StaticFiles(directory=WORK_DIR), name="files")

class FileContent(BaseModel):
    content: str

class CreateItem(BaseModel):
    path: str
    is_dir: bool

class RenameItem(BaseModel):
    old_path: str
    new_name: str



class ChatCreate(BaseModel):
    name: str

class ChatRename(BaseModel):
    chat_id: str
    new_name: str

class SendMessage(BaseModel):
    content: str

class DeleteItem(BaseModel):
    path: str

class MoveItem(BaseModel):
    source: str
    destination: str


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
            # Ignore .git and cache folders
            if entry.name == '.git' or entry.name in ['__pycache__', 'venv', 'node_modules', '.idea', '.vscode']:
                continue
            
            item = {
                "name": entry.name,
                "path": os.path.relpath(entry.path, WORK_DIR).replace("\\\\", "/"),
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

@app.post("/api/fs/create")
def create_item(data: CreateItem):
    """Create a new file or folder."""
    full_path = os.path.abspath(os.path.join(WORK_DIR, data.path))
    if not full_path.startswith(WORK_DIR):
        raise HTTPException(status_code=403, detail="Access denied")
    if os.path.exists(full_path):
        raise HTTPException(status_code=400, detail="Item already exists")
    
    try:
        if data.is_dir:
            os.makedirs(full_path, exist_ok=True)
        else:
            # Create subdirectories if they don't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fs/rename")
def rename_item(data: RenameItem):
    """Rename a file or folder."""
    old_full = os.path.abspath(os.path.join(WORK_DIR, data.old_path))
    if not old_full.startswith(WORK_DIR) or not os.path.exists(old_full):
        raise HTTPException(status_code=404, detail="Original item not found or access denied")
    
    # new_name is just the basename, so we place it in the same directory
    new_full = os.path.join(os.path.dirname(old_full), data.new_name)
    if os.path.exists(new_full):
        raise HTTPException(status_code=400, detail="Target name already exists")
    
    try:
        os.rename(old_full, new_full)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/fs/delete")
def delete_item(data: DeleteItem):
    """Delete a file or folder."""
    full_path = os.path.abspath(os.path.join(WORK_DIR, data.path))
    if not full_path.startswith(WORK_DIR) or not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Item not found")
    
    try:
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fs/download")
def download_item(path: str):
    """Download a file."""
    full_path = os.path.abspath(os.path.join(WORK_DIR, path))
    if not full_path.startswith(WORK_DIR) or not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(full_path, media_type='application/octet-stream', filename=os.path.basename(full_path))


@app.post("/api/fs/upload")
async def upload_file(path: str = Form(""), file: UploadFile = File(...)):
    # if path is empty, upload to WORK_DIR
    target_dir = os.path.abspath(os.path.join(WORK_DIR, path))
    if not target_dir.startswith(WORK_DIR):
        raise HTTPException(status_code=403, detail="Access denied")
    os.makedirs(target_dir, exist_ok=True)
    
    full_path = os.path.join(target_dir, file.filename)
    try:
        content = await file.read()
        with open(full_path, "wb") as f:
            f.write(content)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fs/move")
def move_item(data: MoveItem):
    src_full = os.path.abspath(os.path.join(WORK_DIR, data.source))
    dst_full = os.path.abspath(os.path.join(WORK_DIR, data.destination))
    
    if not src_full.startswith(WORK_DIR) or not dst_full.startswith(WORK_DIR):
        raise HTTPException(status_code=403, detail="Access denied")
    if not os.path.exists(src_full):
        raise HTTPException(status_code=404, detail="Source not found")
        
    # If destination is a file, use its parent directory
    if os.path.isfile(dst_full):
        dst_full = os.path.dirname(dst_full)
        
    # If destination is an existing directory, move into it
    if os.path.isdir(dst_full):
        dst_full = os.path.join(dst_full, os.path.basename(src_full))
        
    if src_full == dst_full:
        return {"status": "success"}
        
    if os.path.exists(dst_full):
        raise HTTPException(status_code=400, detail="Target file already exists")
        
    try:
        import shutil
        shutil.move(src_full, dst_full)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


CHATS_DIR = os.path.join(WORK_DIR, "chats")
os.makedirs(CHATS_DIR, exist_ok=True)
UPLOAD_DIR = os.path.join(WORK_DIR, "Uploaded_Files")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/api/chat")
def get_chats():
    chats = []
    for filename in os.listdir(CHATS_DIR):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(CHATS_DIR, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    chats.append({"id": data.get("id"), "name": data.get("name")})
            except:
                pass
    # sort by modification time descending
    chats.sort(key=lambda x: os.path.getmtime(os.path.join(CHATS_DIR, x["id"]+".json")), reverse=True)
    return chats

@app.post("/api/chat")
def create_chat(data: ChatCreate):
    chat_id = str(uuid.uuid4())
    chat_data = {"id": chat_id, "name": data.name, "messages": []}
    with open(os.path.join(CHATS_DIR, f"{chat_id}.json"), "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)
    return chat_data

@app.put("/api/chat/rename")
def rename_chat(data: ChatRename):
    path = os.path.join(CHATS_DIR, f"{data.chat_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Chat not found")
    with open(path, "r", encoding="utf-8") as f:
        chat_data = json.load(f)
    chat_data["name"] = data.new_name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)
    return {"status": "success"}

@app.get("/api/chat/{chat_id}")
def get_chat(chat_id: str):
    path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Chat not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.delete("/api/chat/{chat_id}")
def delete_chat(chat_id: str):
    path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(path):
        import os
        os.remove(path)
    return {"status": "success"}

@app.post("/api/chat/{chat_id}/message")

def send_message(chat_id: str, data: SendMessage):
    path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Chat not found")
        
    with open(path, "r", encoding="utf-8") as f:
        chat_data = json.load(f)
        
    # Append user message
    user_msg = {"role": "user", "content": data.content}
    chat_data["messages"].append(user_msg)
    
    # Save user msg immediately so UI feels responsive or if process fails
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)

    # Call OpenClaw agent
    import subprocess
    try:
        result = subprocess.run(
            ["openclaw", "agent", "--session-id", f"webchat_{chat_id}", "--message", data.content, "--json"],
            capture_output=True,
            text=True,
            check=True
        )
        output_json = json.loads(result.stdout)
        ai_text = output_json.get("result", {}).get("payloads", [{}])[0].get("text", "(No response generated)")
    except Exception as e:
        ai_text = f"(System Error: Failed to contact OpenClaw Agent. {str(e)})"
    
    ai_msg = {"role": "assistant", "content": ai_text}
    chat_data["messages"].append(ai_msg)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)
        
    return {"user_message": user_msg, "assistant_message": ai_msg}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)