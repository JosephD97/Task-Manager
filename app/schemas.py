#этот файл нужен для определения правил передачи данных

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

#схемы для задач Tasks

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    deadline: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass  #когда мы создаем задачу, нам нужно то же самое, что в Base

class Task(TaskBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

#cхемы для Users

class UserBase(BaseModel):#присылает нам email и password
    email: EmailStr

class UserCreate(UserBase):#мы отдаем юзеру его id и email
    password: str 

class User(UserBase):
    id: int
    is_active: bool
    tasks: List[Task] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None