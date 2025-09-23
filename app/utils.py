# app/utils.py
import os
from datetime import datetime
from pathlib import Path

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_upload_file_tmp(upload_file, destination: Path = None) -> str:
    """
    Save FastAPI UploadFile to disk and return filepath.
    """
    if destination is None:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        filename = f"{timestamp}_{upload_file.filename}"
        destination = UPLOAD_DIR / filename
    else:
        filename = destination.name

    with destination.open("wb") as buffer:
        for chunk in iter(lambda: upload_file.file.read(1024 * 1024), b""):
            buffer.write(chunk)
    return str(destination)
