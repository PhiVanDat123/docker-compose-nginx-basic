from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
import hashlib, secrets, uuid

app = FastAPI(title="Task Manager API", version="1.0.0")

# ── Enums & Schemas ──────────────────────────────────────────────────────────

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Priority = Priority.medium
    due_date: Optional[str] = Field(None, description="YYYY-MM-DD")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    done: Optional[bool] = None
    due_date: Optional[str] = None

# ── In-memory DB ─────────────────────────────────────────────────────────────

users_db: Dict[str, dict] = {}   # user_id -> user
tokens_db: Dict[str, str] = {}   # token   -> user_id
tasks_db: Dict[str, dict] = {}   # task_id -> task

def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def _id() -> str:
    return str(uuid.uuid4())[:8]

# ── Auth dependency ───────────────────────────────────────────────────────────

def current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    user_id = tokens_db.get(authorization.removeprefix("Bearer "))
    if not user_id or user_id not in users_db:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return users_db[user_id]

# ── Auth endpoints ────────────────────────────────────────────────────────────

@app.post("/auth/register", status_code=201, tags=["Auth"])
def register(body: UserRegister):
    """Đăng ký tài khoản mới."""
    if any(u["username"] == body.username for u in users_db.values()):
        raise HTTPException(status_code=409, detail="Username already taken")
    uid = _id()
    users_db[uid] = {
        "id": uid, "username": body.username,
        "full_name": body.full_name, "password_hash": _hash(body.password),
        "created_at": _now(),
    }
    return {"id": uid, "username": body.username, "message": "Registered successfully"}

@app.post("/auth/login", tags=["Auth"])
def login(body: UserLogin):
    """Đăng nhập, nhận Bearer token."""
    user = next((u for u in users_db.values() if u["username"] == body.username), None)
    if not user or user["password_hash"] != _hash(body.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = secrets.token_hex(32)
    tokens_db[token] = user["id"]
    return {"access_token": token, "token_type": "bearer", "user_id": user["id"]}

@app.post("/auth/logout", tags=["Auth"])
def logout(authorization: Optional[str] = Header(None), user: dict = Depends(current_user)):
    """Đăng xuất, huỷ token."""
    tokens_db.pop(authorization.removeprefix("Bearer "), None)
    return {"message": f"Goodbye, {user['username']}!"}

@app.get("/auth/me", tags=["Auth"])
def me(user: dict = Depends(current_user)):
    """Xem thông tin tài khoản hiện tại."""
    return {k: v for k, v in user.items() if k != "password_hash"}

# ── Task endpoints ────────────────────────────────────────────────────────────

@app.get("/tasks", tags=["Tasks"])
def list_tasks(
    done: Optional[bool] = None,
    priority: Optional[Priority] = None,
    search: Optional[str] = None,
    user: dict = Depends(current_user),
):
    """Lấy danh sách tasks. Hỗ trợ filter theo done, priority và tìm kiếm."""
    result = [t for t in tasks_db.values() if t["owner_id"] == user["id"]]
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if priority:
        result = [t for t in result if t["priority"] == priority]
    if search:
        kw = search.lower()
        result = [t for t in result if kw in t["title"].lower()
                  or (t["description"] and kw in t["description"].lower())]
    return {"total": len(result), "tasks": result}

@app.post("/tasks", status_code=201, tags=["Tasks"])
def create_task(body: TaskCreate, user: dict = Depends(current_user)):
    """Tạo task mới."""
    tid = _id()
    task = {**body.model_dump(), "id": tid, "done": False,
            "owner_id": user["id"], "created_at": _now()}
    tasks_db[tid] = task
    return task

@app.get("/tasks/{task_id}", tags=["Tasks"])
def get_task(task_id: str, user: dict = Depends(current_user)):
    """Lấy chi tiết một task."""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["owner_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return task

@app.patch("/tasks/{task_id}", tags=["Tasks"])
def update_task(task_id: str, body: TaskUpdate, user: dict = Depends(current_user)):
    """Cập nhật task (partial update)."""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["owner_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    task.update({k: v for k, v in body.model_dump().items() if v is not None})
    task["updated_at"] = _now()
    return task

@app.delete("/tasks/{task_id}", tags=["Tasks"])
def delete_task(task_id: str, user: dict = Depends(current_user)):
    """Xoá một task."""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["owner_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    del tasks_db[task_id]
    return {"message": "Task deleted", "id": task_id}

@app.post("/tasks/{task_id}/toggle", tags=["Tasks"])
def toggle_task(task_id: str, user: dict = Depends(current_user)):
    """Toggle trạng thái done / not done."""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["owner_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    task["done"] = not task["done"]
    task["updated_at"] = _now()
    return task

@app.get("/tasks/stats/summary", tags=["Tasks"])
def task_summary(user: dict = Depends(current_user)):
    """Thống kê nhanh: tổng, hoàn thành, còn lại, theo priority."""
    my = [t for t in tasks_db.values() if t["owner_id"] == user["id"]]
    return {
        "total": len(my),
        "done": sum(1 for t in my if t["done"]),
        "pending": sum(1 for t in my if not t["done"]),
        "by_priority": {p.value: sum(1 for t in my if t["priority"] == p) for p in Priority},
    }

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["General"])
def health():
    return {"status": "ok", "timestamp": _now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)