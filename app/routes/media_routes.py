# app/routes/media_routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import aiofiles
from uuid import uuid4

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
    """
    Replace this with actual AI processing logic.
    For images/videos: detect crop disease, health, etc.
    """
    # Example dummy result
    return {"status": "processed", "message": "AI analysis complete", "recommendation": "Water crop more"}

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Validate file size
    file_size = 0
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
    
    # Close the uploaded file
    await file.close()

    # Trigger AI processing
    ai_result = await process_file_with_ai(file_path)

    return {
        "filename": unique_filename,
        "path": file_path,
        "ai_result": ai_result
    }

@router.get("/view/{filename}")
async def view_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)