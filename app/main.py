# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models
from .database import Base, engine, get_db
from .models import User
from .schemas import UserBase, UserCreate, UserLogin, Token, UserUpdate
from .auth import get_password_hash, verify_password, create_access_token, get_current_user,router


# Create DB tables on startup
models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="AI Farm CoPilot - Backend (Hackathon)")
app.include_router(router)
# Create tables after all models are loaded
# ---------------------------
# AUTH ROUTES
# ---------------------------

# Register
@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check duplicate username/email
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password,
                   full_name=user.full_name,phone_number=user.phone_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

# Login
@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

# ---------------------------
# USER ROUTES
# ---------------------------

# Current user info
@app.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

@app.get("/profile", response_model=UserBase)
def get_profile(current_user: User = Depends(get_current_user)):
    """Fetch current user's profile"""
    return current_user

@app.put("/profile/update", response_model=UserBase)
def update_profile(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ):
    """Update current user's profile (email, phone, etc). Role only if admin."""
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only admins can update roles
    if update_data.role and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update roles")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user
# ---------------------------
# FARM ROUTES (MVP)
# ---------------------------

@app.post("/farm/add")
def add_farm(
    farm_name: str,
    location: str,
    soil_type: str,
    area: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # For now just return as response (DB model for Farm can be added later)
    return {
        "msg": "Farm added successfully",
        "owner": current_user.username,
        "farm": {
            "farm_name": farm_name,
            "location": location,
            "soil_type": soil_type,
            "area": area
        }
    }
