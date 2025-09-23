# app/schemas.py
from pydantic import BaseModel
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
