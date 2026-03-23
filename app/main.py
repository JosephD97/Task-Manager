from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, get_db
from . import models, schemas, crud, auth
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#проверит базу и создаст таблицы, если их нет
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager")

@app.get("/")
def home():
    return {"status": "Work in progress", "project": "Task Manager"}

@app.get("/users/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    return {"token": token}


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

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm=Depends(),
    db: Session=Depends(get_db)):
    #поиск пользователя по email
    user=crud.get_user_by_email(db, email=form_data.username)
    #проверка на существование такого пользователя и на совпадение пароля
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException (status_code=401, detail="Incorrect email or password")
    #создание токена
    access_token = auth.create_access_token(data={"sub": user.email})
    #возврат токена
    return {"access_token": access_token, "token_type": "bearer"}

