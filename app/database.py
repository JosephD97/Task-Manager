from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# connect_args={"check_same_thread": False} если SQLite, но у меня postgres поэтому не нужен
'''engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)'''


# создание движка, который связывает python и postgres
engine = create_engine(settings.DATABASE_URL) 

#SessionLocal = sessionmaker  объект который может создавать сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)

#autocommit=False запрещает автоматическую отправку данных в БД
#autoflush=False  ручное подтверждение изменений
#bind=engine      соединает сессию к подключению к БД


#родительский класс, все таблицы будут наследоваться от него Base
Base = declarative_base()
#Base класс который создаётся функцией declarative_base()


#открывает и закрывает сессию перед и после запроса
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()