from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, get_db
from . import models, schemas, crud, auth
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt # Добавь этот импорт в самое начало файла!


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#функция для определения клиента, который посылает запрос
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        #расшифровка токена, используя SECRET_KEY
        payload = jwt.decode(token, auth.settings.SECRET_KEY, algorithms=[auth.settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    #поиск юзера в базе
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user





#проверит базу и создаст таблицы, если их нет
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager")

#домашняя страница
@app.get("/")
def home():
    return {"status": "Work in progress", "project": "Task Manager"}

#позволяет залогиненному пользователю получить свои данные
@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

#первый вариант ниже обновленная версия
'''@app.get("/tasks/", response_model=list[schemas.Task])
def read_my_tasks(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_my_tasks(db=db, user_id=current_user.id)'''

#получение списка задач
@app.get("/tasks/", response_model=list[schemas.Task])
def read_my_tasks(
    status: str = None, 
    overdue: bool = None, 
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    #передаем всё, что прислал пользователь в CRUD
    return crud.get_my_tasks(
        db=db, 
        user_id=current_user.id, 
        status=status, 
        overdue=overdue, 
        skip=skip, 
        limit=limit
    )



#регистрация
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

#вход и получение токена
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

#создание задачи
@app.post("/tasks/", response_model=schemas.Task)
def create_new_task(
    task: schemas.TaskCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user) # Вот здесь проверка токена!
):
    return crud.create_task(db=db, task=task, user_id=current_user.id)

#удаление задачи
@app.delete("/tasks/{task_id}")
def delete_my_task(
    task_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    success = crud.delete_task(db=db, task_id=task_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

#обновление статуса (PATCH)
@app.patch("/tasks/{task_id}")
def update_task(
    task_id: int, 
    status: str, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    updated_task = crud.update_task_status(db=db, task_id=task_id, status=status, user_id=current_user.id)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task