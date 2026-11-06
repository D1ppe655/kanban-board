from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")
CSV_FILE = "tasks.csv"

# --- МОДЕЛИ ДАННЫХ ---
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    status: str # "todo", "in_progress", "done"

# --- STORAGE (Работа с CSV) ---
def load_tasks():
    if not os.path.exists(CSV_FILE):
        # Создаем пустой файл, если его нет
        df = pd.DataFrame(columns=["id", "title", "status"])
        df.to_csv(CSV_FILE, index=False)
        return df
    try:
        return pd.read_csv(CSV_FILE)
    except Exception:
        # Если файл битый (например, открыт в Excel), возвращаем пустой
        return pd.DataFrame(columns=["id", "title", "status"])

def save_tasks(df):
    try:
        df.to_csv(CSV_FILE, index=False)
    except PermissionError:
        raise HTTPException(status_code=500, detail="Файл заблокирован другим процессом")

# --- API ЭНДПОИНТЫ ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/tasks")
async def get_tasks():
    df = load_tasks()
    return df.to_dict(orient="records")

@app.post("/tasks")
async def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Название задачи не может быть пустым")
    
    df = load_tasks()
    new_id = 1 if df.empty else int(df["id"].max()) + 1
    new_row = pd.DataFrame([{"id": new_id, "title": task.title, "status": "todo"}])
    df = pd.concat([df, new_row], ignore_index=True)
    save_tasks(df)
    return {"message": "Task created", "id": new_id}

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    df = load_tasks()
    if task_id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    if task.status not in ["todo", "in_progress", "done"]:
        raise HTTPException(status_code=400, detail="Неверный статус")

    df.loc[df["id"] == task_id, "status"] = task.status
    save_tasks(df)
    return {"message": "Task updated"}