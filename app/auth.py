#хеширование (чтобы не хранить пароли в открытом виде)

from passlib.context import CryptContext

#способа шифрования bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#bcrypt стандартный алгоритм для шифрования

#функция которая делает из пароля хеш
def get_password_hash(password):
    return pwd_context.hash(password)

# функция которая проверяет: подходит ли пароль к хешу (нужна для логина)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)