from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, get_db
from . import models, schemas, crud

#проверит базу и создаст таблицы, если их нет
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager")

@app.get("/")
def home():
    return {"status": "Work in progress", "project": "Task Manager"}

@app.post("/register", response_model=schemas.User)
#response_model это мера безопасности. 
#если функция вернет объект с паролем, то пароль отрежется и останется только id и email
def register_user(user: schemas.UserCreate, db: Session=Depends(get_db)):
    #проверка пользователся с таким же email
    db_user=crud.get_user_by_email(db,email=user.email)
    if db_user:
        raise HTTPException(status_code=400,detail="Email already registered")
    #если email уникальный, то создаем пользователя
    return crud.create_user(db=db, user=user)

