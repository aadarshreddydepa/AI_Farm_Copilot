from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ---------------------
# AUTH / USER SCHEMAS
# ---------------------

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


class UserProfile(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    created_at: datetime

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    created_at: datetime

    class Config:
        orm_mode = True  # allows SQLAlchemy model → Pydantic conversion

# ---------------------
# FARM SCHEMAS
# ---------------------

class FarmCreate(BaseModel):
    farm_name: str
    location: Optional[str] = None
    soil_type: Optional[str] = None
    area: Optional[float] = None


class FarmResponse(FarmCreate):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        orm_mode = True
