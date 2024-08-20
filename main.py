from fastapi import FastAPI, BackgroundTasks
from task import generate_synthetic_data

app = FastAPI()

@app.post("/generate/")
async def generate_data(param1: str, param2: str, background_tasks: BackgroundTasks):
    task = generate_synthetic_data.delay(param1, param2)
    background_tasks.add_task(check_task_status, task.id)
    return {"task_id": task.id, "status": "Processing"}

async def check_task_status(task_id):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    if result.state == "SUCCESS":
        print(f"Task {task_id} completed with result: {result.result}")
    elif result.state == "FAILURE":
        print(f"Task {task_id} failed")
