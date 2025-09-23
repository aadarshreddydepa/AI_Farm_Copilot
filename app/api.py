# app/api.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
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

@router.post("/upload/", response_model=schemas.ImageRecordOut)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # validate content type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")
    # save file
    filepath = save_upload_file_tmp(file)
    rec = crud.create_image_record(db, filename=file.filename, filepath=filepath)
    # read bytes for inference
    file.file.seek(0)
    image_bytes = open(filepath, "rb").read()
    pred = inference.predict_image_bytes(image_bytes)
    pred_str = f"{pred['label']} (score={pred['score']:.3f})"
    rec = crud.update_image_prediction(db, rec.id, pred_str)
    return rec

@router.get("/images/", response_model=List[schemas.ImageRecordOut])
def list_images(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_images(db, skip=skip, limit=limit)

@router.get("/images/{record_id}", response_model=schemas.ImageRecordOut)
def get_image(record_id: int, db: Session = Depends(get_db)):
    rec = crud.get_image(db, record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Image not found.")
    return rec
