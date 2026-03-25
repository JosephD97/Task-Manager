#это файл для работы с базой данных

from sqlalchemy.orm import Session
from . import models, schemas, auth
from datetime import datetime

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
    db.refresh(db_user) #обновляет объект db_user данными из базы чтобы увидеть id
    
    return db_user

# Функция для создания задачи
def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    # .model_dump() превращает Pydantic-схему в обычный словарь Python
    db_task = models.Task(**task.model_dump(), owner_id=user_id) #**task.model_dump() - это “распаковка словаря” в аргументы
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

#функция для получения ВСЕХ задач пользователя
#def get_my_tasks(db: Session, user_id: int):
#    return db.query(models.Task).filter(models.Task.owner_id == user_id).all()


#функция для получения списка задач пользователя с фильтрами и пагинацией
def get_my_tasks(db: Session, user_id: int, status: str = None, overdue: bool = None, skip: int = 0, limit: int = 10):
    #начало запроса
    query = db.query(models.Task).filter(models.Task.owner_id == user_id)
    
    #фильтрация по статусу (todo, in_progress, done)
    if status:
        query = query.filter(models.Task.status == status)

    #фильтрация по просроченным задачам (overdue)
    if overdue is True:
        #поиск задачь, где дедлайн уже прошел (меньше текущего времени) и статус не "done"
        query = query.filter(
            models.Task.deadline < datetime.utcnow(),
            models.Task.status != "done"
        )
    elif overdue is False:
        #поиск только тех задачь, у которых дедлайн еще впереди
        query = query.filter(models.Task.deadline >= datetime.utcnow())

    #пагинация: skip — сколько пропустить, limit — сколько взять
    return query.offset(skip).limit(limit).all()


#функция для удаления задачи
def delete_task(db: Session, task_id: int, user_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == user_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task

#функция для изменения статуса (например, с "todo" на "done")
def update_task_status(db: Session, task_id: int, status: str, user_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == user_id).first()
    if db_task:
        db_task.status = status
        db.commit()
        db.refresh(db_task)
    return db_task