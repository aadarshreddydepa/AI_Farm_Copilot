# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def create_image_record(db: Session, filename: str, filepath: str, uploaded_by: int = None):
    rec = models.ImageRecord(filename=filename, filepath=filepath, uploaded_by=uploaded_by)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def update_image_prediction(db: Session, record_id: int, prediction: str):
    rec = db.query(models.ImageRecord).filter(models.ImageRecord.id == record_id).first()
    if not rec:
        return None
    rec.prediction = prediction
    db.commit()
    db.refresh(rec)
    return rec

def get_image(db: Session, record_id: int):
    return db.query(models.ImageRecord).filter(models.ImageRecord.id == record_id).first()

def list_images(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ImageRecord).offset(skip).limit(limit).all()
