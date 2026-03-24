#функции для работы с базой

from sqlalchemy.orm import Session
from . import models, schemas, auth

#поиск пользователя по email (нужно для проверки при регистрации)
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

#создание нового пользователя
def create_user(db: Session, user: schemas.UserCreate):
    #хеширование пароля из схемы UserCreate
    hashed_pw = auth.get_password_hash(user.password)
    
    #объект модели SQLAlchemy
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_pw
    )
    
    #сохранение в Postgres
    db.add(db_user)
    db.commit() #сохранение изменений в бд
    db.refresh(db_user)#обновляет объект db_user данными из базы чтобы увидеть id
    
    return db_user

# Функция для создания задачи
def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    # .model_dump() превращает Pydantic-схему в обычный словарь Python
    db_task = models.Task(**task.model_dump(), owner_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Функция для получения ВСЕХ задач именно этого пользователя
def get_my_tasks(db: Session, user_id: int):
    return db.query(models.Task).filter(models.Task.owner_id == user_id).all()