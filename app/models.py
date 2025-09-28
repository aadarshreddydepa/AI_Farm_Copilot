# app/models.py
from sqlalchemy import Column, Float, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)  # <- make sure this is here
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    role = Column(String, default="farmer")   # farmer, agronomist, admin
    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    farm_name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    soil_type = Column(String, nullable=True)
    area = Column(Float, nullable=True)  # in acres or hectares
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationship back to User
    owner = relationship("User", back_populates="farms")
    farms = relationship("Farm", back_populates="owner")
