from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

app = FastAPI()

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    age: Optional[int] = Field(None, ge=1, description="Возраст пользователя")
    is_subscribed: Optional[bool] = Field(False, description="Подписка на рассылку")
    
    @field_validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Имя не может быть пустым')
        return v.strip()

@app.post("/create_user", response_model=UserCreate)
async def create_user(user: UserCreate):
    """
    Создает нового пользователя.
    Принимает JSON с данными пользователя и возвращает их.
    """
    return user
    
