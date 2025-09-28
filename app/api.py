# app/api.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session # type: ignore
from typing import List

from . import crud, schemas
from .database import SessionLocal
from .utils import save_upload_file_tmp
from .ml import inference

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
