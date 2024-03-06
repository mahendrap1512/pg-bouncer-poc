from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from datetime import datetime
from db import Task, SessionLocal, engine
from constants import TaskStatus
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from redis_manager import get_redis_client


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
        NON_RESPONSE_WAIT_TIME = 10  # seconds
        channel_name = "share"
        pubsub = get_redis_client().pubsub()
        # Need is_init, since at the time of API call if there were no message in past 10 seconds, it will go to the else part
        # we are only interested in, if post calling this API, if there is no message for 10 seconds, then terminate the API
        # Another approach can be just create a new  aioredis instance inside the API call, itself, then we will not need is_init variable
        is_init = True
        # client.subscribe(channel_name)
        # pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel_name)
        lc = 1

        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            print('loop counter', lc)
            lc += 1
            # Checks for new messages and return them to client if any
            message = await pubsub.get_message(timeout=NON_RESPONSE_WAIT_TIME)
            if message and message['type'] == 'message':
                print('msg ', message)
                val = message['data'].decode('utf-8')
                print(val)
                yield val
            else:
                if is_init:
                    is_init = False
                else:
                    break




    return EventSourceResponse(event_generator())