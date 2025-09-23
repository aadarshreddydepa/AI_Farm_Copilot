# app/main.py
from fastapi import FastAPI
from .api import router
from .database import engine
from . import models

app = FastAPI(title="AI Farm CoPilot - Backend (Hackathon)")

app.include_router(router)

# Create DB tables on startup (quick hackathon-friendly)
@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)
