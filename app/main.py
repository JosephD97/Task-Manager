from fastapi import FastAPI
from .database import engine
from . import models

#проверит базу и создаст таблицы, если их нет
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager")

@app.get("/")
def home():
    return {"status": "Work in progress", "project": "Task Manager"}