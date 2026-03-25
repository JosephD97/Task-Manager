#этот файл нужен, чтобы не писать важные настройки (пароли, ключи, адреса баз данных) прямо в коде
#а так же дает централизованное управление изменениями (меняю в одном файле, но изменения подхватывают все)

import os
from dotenv import load_dotenv

#эта команда ищет файл .env в папке проекта и загружает его содержимое в "окружение" (environment) операционной системы.
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Task Manager API" #название проекта
    DATABASE_URL: str = os.getenv("DATABASE_URL") #подключения к базе данных
    SECRET_KEY: str = os.getenv("SECRET_KEY") #безопасность (используется для подписи JWT-токенов и проверки их подлинности)
    ALGORITHM: str = os.getenv("ALGORITHM") #алгоритм для подписи JWT
    #все данные из .env текстовые, а время нужно для расчетов, поэтому переводим время в число 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

#создаем один экземпляр класса, который будем импортировать в другие файлы.
settings = Settings()