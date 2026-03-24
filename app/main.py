from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, get_db
from . import models, schemas, crud, auth
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt # Добавь этот импорт в самое начало файла!


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- ЭТОЙ ФУНКЦИИ У ТЕБЯ НЕ ХВАТАЛО ---
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Расшифровываем токен, используя наш SECRET_KEY
        payload = jwt.decode(token, auth.settings.SECRET_KEY, algorithms=[auth.settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Ищем юзера в базе
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user





#проверит базу и создаст таблицы, если их нет
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager")

@app.get("/")
def home():
    return {"status": "Work in progress", "project": "Task Manager"}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Посмотреть свои задачи
@app.get("/tasks/", response_model=list[schemas.Task])
def read_my_tasks(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_my_tasks(db=db, user_id=current_user.id)

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

# Создать задачу (нужен токен!)
@app.post("/tasks/", response_model=schemas.Task)
def create_new_task(
    task: schemas.TaskCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user) # Вот здесь проверка токена!
):
    return crud.create_task(db=db, task=task, user_id=current_user.id)

