#хеширование (чтобы не хранить пароли в открытом виде)

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from .config import settings

#способа шифрования bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#bcrypt стандартный алгоритм для шифрования

#функция которая делает из пароля хеш
def get_password_hash(password):
    return pwd_context.hash(password)

# функция которая проверяет: подходит ли пароль к хешу (нужна для логина)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#создание JWT-токена доступа (нужно для того чтобы на каждое действие не спрашивать логин и пароль, если пользователь уже залогинен)
def create_access_token(data:dict):
    to_encode=data.copy()#копирует входные данные, чтобы не менять оригинал (так безопаснее)
    #срок годности токена
    expire=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    #шифрование данных с помощью секретного ключа из .env (чтобы никто не мог изменить данные внутри токена, типа как печать на бумаге)
    encoded_jwt=jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt