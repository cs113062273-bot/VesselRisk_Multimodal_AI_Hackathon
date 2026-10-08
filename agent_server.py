import os
import sys
import argparse
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Universal Local Coding Agent",
    version="1.0.0",
    description="Local Autonomous Coding Agent for ChatGPT Web & MCP"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 預設為指令執行的當前目錄 (Current Working Directory)，絕無硬編碼
CURRENT_WORKSPACE = os.path.abspath(os.getcwd())

class FileContent(BaseModel):
    path: str
    content: str

class Command(BaseModel):
    cmd: str

class WorkspaceReq(BaseModel):
    workspace_path: str

@app.get("/get_workspace", summary="Get current active workspace directory")
def get_workspace():
    return {"current_workspace": CURRENT_WORKSPACE}

@app.post("/set_workspace", summary="Switch active workspace directory on the fly")
def set_workspace(req: WorkspaceReq):
    global CURRENT_WORKSPACE
    # 支援 ~/ 符號自動展開（相容 Mac / Linux / Windows）
    expanded = os.path.expanduser(req.workspace_path)
    target = os.path.abspath(expanded)
    if not os.path.exists(target):
        raise HTTPException(404, f"Directory does not exist: {target}")
    CURRENT_WORKSPACE = target
    return {"status": "success", "switched_to": CURRENT_WORKSPACE}

@app.get("/list_files", summary="List files and folders in active workspace")
def list_files(subpath: str = ""):
    target = os.path.abspath(os.path.join(CURRENT_WORKSPACE, subpath))
    if not target.startswith(CURRENT_WORKSPACE):
        raise HTTPException(400, "Access denied")
    if not os.path.exists(target):
        raise HTTPException(404, f"Directory not found: {target}")
    return {"workspace": CURRENT_WORKSPACE, "subpath": subpath, "items": os.listdir(target)}

@app.get("/read_file", summary="Read file content from active workspace")
def read_file(path: str):
    target = os.path.abspath(os.path.join(CURRENT_WORKSPACE, path))
    if not target.startswith(CURRENT_WORKSPACE) or not os.path.exists(target):
        raise HTTPException(404, f"File not found: {target}")
    try:
        with open(target, "r", encoding="utf-8", errors="ignore") as f:
            return {"path": path, "content": f.read()}
    except Exception as e:
        raise HTTPException(500, f"Error reading file: {str(e)}")

@app.post("/write_file", summary="Create or overwrite a file in active workspace")
def write_file(data: FileContent):
    target = os.path.abspath(os.path.join(CURRENT_WORKSPACE, data.path))
    if not target.startswith(CURRENT_WORKSPACE):
        raise HTTPException(400, "Access denied")
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(data.content)
        return {"status": "success", "file": data.path, "full_path": target}
    except Exception as e:
        raise HTTPException(500, f"Error writing file: {str(e)}")

@app.get("/", summary="Root health check")
@app.get("/health", summary="Health check endpoint")
def health_check():
    return {"status": "ok", "workspace": CURRENT_WORKSPACE}

@app.post("/run_terminal", summary="Execute terminal command in active workspace")
def run_terminal(data: Command):
    if any(danger in data.cmd for danger in ["format", "rm -rf /", "del /f /s /q C:\\"]):
        raise HTTPException(400, "Dangerous command rejected")
    try:
        res = subprocess.run(
            data.cmd,
            shell=True,
            cwd=CURRENT_WORKSPACE,
            capture_output=True,
            timeout=120
        )
        
        def safe_decode(b: bytes) -> str:
            if not b:
                return ""
            for enc in ["utf-8", "cp950", "gbk", "latin-1"]:
                try:
                    return b.decode(enc)
                except UnicodeDecodeError:
                    continue
            return b.decode("utf-8", errors="replace")

        return {
            "stdout": safe_decode(res.stdout),
            "stderr": safe_decode(res.stderr),
            "exit_code": res.returncode,
            "cwd": CURRENT_WORKSPACE
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(408, "Command execution timed out after 120s")
    except Exception as e:
        raise HTTPException(500, f"Execution failed: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Local Coding Agent")
    parser.add_argument("--workspace", type=str, default="", help="Target workspace directory")
    args = parser.parse_args()
    if args.workspace:
        CURRENT_WORKSPACE = os.path.abspath(os.path.expanduser(args.workspace))
    print(f"[*] Agent Server Online! Active Workspace: {CURRENT_WORKSPACE}")
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
