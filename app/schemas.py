# app/schemas.py
from pydantic import BaseModel,EmailStr
from typing import Optional
from datetime import datetime

class ImageRecordCreate(BaseModel):
    filename: str

class ImageRecordOut(BaseModel):
    id: int
    filename: str
    filepath: str
    prediction: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True