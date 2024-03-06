from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from datetime import datetime
from db import Task, SessionLocal, engine
from constants import TaskStatus
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from redis_manager import redis_client
import asyncio


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TaskBase(BaseModel):
    name: str
    description: str
    status :  TaskStatus = TaskStatus.PLANNED

    class Config:
        from_attributes = True


@app.post('/tasks/')
async def create_task(task: TaskBase, db: Session = Depends(get_db)):
    task = Task(**task.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get('/tasks/')
async def get_tasks(db: Session = Depends(get_db)):
    import random
    task_id = random.randint(0, 100)
    curr_time = datetime.utcnow()
    print(curr_time)
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        task = Task(name=f"task {task_id}", description=f"task {task_id} description",)
        db.add(task)
        db.commit()
        db.refresh(task)

    return task


@app.get("/new-tasks/")
async def new_tasks():
    with engine.connect() as conn:
        query = "INSERT INTO tasks(name, description) VALUES ('abc', 'def')"
        # query2 = "SELECT * FROM tasks"
        # num =  random.randint(1, 1000)
        # query = f"SELECT * FROM document_classification where created_date < '2023-05-15 09:26:19.233'"
        conn.execute(query)





@app.get('/stream/{id}/')
async def message_stream(request: Request, id: int):
    async def event_generator():
        STREAM_DELAY = 0.1  # second
        NON_RESPONSE_WAIT_TIME = 10  # seconds
        last_event_time = datetime.now()
        channel_name = "share"
        pubsub = redis_client.pubsub()
        pubsub.subscribe(channel_name)

        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break

            # Checks for new messages and return them to client if any
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                val = message['data'].decode('utf-8')
                print(val)
                last_event_time = datetime.now()
                yield val

            curr_time = datetime.now()

            time_diff_in_ms = (curr_time - last_event_time).total_seconds()
            if time_diff_in_ms > NON_RESPONSE_WAIT_TIME:
                break

            # Prefer Some delay otherwise this while loop will be so expensive
            await asyncio.sleep(STREAM_DELAY)



    return EventSourceResponse(event_generator())