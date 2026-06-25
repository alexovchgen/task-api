from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import asyncio


app = FastAPI(title="Task Manager")


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description : str = Field(default="", max_length=2000)


class TaskUpdate(BaseModel):
    title : str | None = Field(default=None, min_length=1, max_length=200)
    description : str | None = Field(default=None, max_length=2000)
    done : bool | None = None


class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False


tasks : dict[int : Task] = {}
next_id : int = 1
MAX_TASKS : int = 100



@app.get('/health')
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post('/tasks', response_model=Task)
async def create_task(payload : TaskCreate) -> Task:
    global next_id

    if len(tasks) >= MAX_TASKS:
        raise HTTPException(status_code=409, detail="Too many tasks")

    task = Task(
        id=next_id,
        title=payload.title,
        description=payload.description,
        done = False
    )

    tasks[task.id] = task   
    next_id += 1
    return task


@app.get('/tasks', response_model=list[Task])
async def list_tasks() -> list[Task]:
    return list(tasks.values())


@app.get('/tasks/{task_id}', response_model=Task)
async def get_task(task_id: int) -> Task:
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch('/tasks/{task_id}', response_model=Task)
async def update_task(task_id: int, payload: TaskUpdate) -> Task:
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = task.model_copy(
        update={ k : v for k, v in payload.model_dump().items() if v is not None }
    )
    tasks[task_id] = updated
    return updated


@app.delete('/tasks/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int) -> None:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del tasks[task_id]
    return None

@app.get('/slow')
async def slow_endpoint():
    await asyncio.sleep(1)
    return {"message": "done"}