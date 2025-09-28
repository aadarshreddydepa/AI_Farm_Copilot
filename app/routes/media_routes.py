from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import aiofiles
from uuid import uuid4
from datetime import datetime
from app.database import get_db
from app import models
from app.auth import get_current_user

router = APIRouter(
    prefix="/media",
    tags=["media"]
)

UPLOAD_DIR = "static/uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mp4", ".mov"}
MAX_FILE_SIZE_MB = 20  # Max 20MB

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# Stub AI processing function
async def process_file_with_ai(file_path: str) -> dict:
    return {"status": "processed", "message": "AI analysis complete", "recommendation": "Water crop more"}


@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Validate file size
    contents = await file.read()
    file_size = len(contents) / (1024 * 1024)  # size in MB
    if file_size > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large. Max {MAX_FILE_SIZE_MB} MB allowed.")

    # Generate unique filename
    unique_filename = f"{uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file asynchronously
    async with aiofiles.open(file_path, "wb") as out_file:
        await out_file.write(contents)
    await file.close()

    # Trigger AI processing
    ai_result = await process_file_with_ai(file_path)

    # Save in DB
    db_media = models.Media(
        filename=unique_filename,
        file_path=file_path,
        file_type=file_ext,
        size_mb=str(round(file_size, 2)),
        uploaded_at=datetime.utcnow(),
        user_id=current_user.id,
        ai_status=ai_result["status"],
        ai_result=str(ai_result)  # could use json.dumps(ai_result)
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)

    return {
        "id": db_media.id,
        "filename": db_media.filename,
        "path": db_media.file_path,
        "size": db_media.size_mb,
        "ai_result": ai_result
    }


@router.get("/myfiles")
def list_my_files(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    files = db.query(models.Media).filter(models.Media.user_id == current_user.id).all()
    return files


@router.get("/view/{filename}")
async def view_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@router.delete("/delete/{media_id}", status_code=204)
def delete_file(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    media = db.query(models.Media).filter(
        models.Media.id == media_id,
        models.Media.user_id == current_user.id
    ).first()

    if not media:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete file from disk
    if os.path.exists(media.file_path):
        os.remove(media.file_path)

    # Delete from DB
    db.delete(media)
    db.commit()

    return {"detail": "File deleted successfully"}
