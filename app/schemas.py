# app/schemas.py
from pydantic import BaseModel,EmailStr
from typing import Optional,List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
class UserResponse(BaseModel):
    id: int
    created_at: datetime
<<<<<<< HEAD

    class Config:
        orm_mode = True
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: str

    class Config:
        orm_mode = True
    
class UserUpdate(BaseModel):
    eamil: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None  

class FarmBase(BaseModel):
    farm_name: str
    location: Optional[str] = None
    soil_type: Optional[str] = None
    area: Optional[float] = None

class FarmCreate(FarmBase):
    pass

class FarmResponse(FarmBase):
    id: int
    owner_id: int
=======
>>>>>>> 07b3d76417b516865314e4859eed80b43ad58a97

    class Config:
        orm_mode = True
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: str

    class Config:
        orm_mode = True
    
class UserUpdate(BaseModel):
    eamil: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = None  