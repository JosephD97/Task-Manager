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