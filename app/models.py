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
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="farmer")  # farmer, agronomist, admin
    created_at = Column(DateTime, default=datetime.utcnow)

    farms = relationship("Farm", back_populates="owner")
class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    farm_name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    soil_type = Column(String, nullable=True)
    area = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="farms")

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # image/video
    size_mb = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Optional: link to user or farm
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)

    # AI results
    ai_status = Column(String, default="pending")  # pending/processed/error
    ai_result = Column(Text, nullable=True)  # JSON or string

    # Relationships
    user = relationship("User", back_populates="media_files")
    farm = relationship("Farm", back_populates="media_files")