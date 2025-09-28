from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.routes import media_routes
from . import models, schemas
from .database import engine, get_db
from .auth import get_password_hash, verify_password, create_access_token, get_current_user
from app import auth

app = FastAPI(title="AI Farm CoPilot - Backend (Hackathon)")

# Create tables
models.Base.metadata.create_all(bind=engine)

# ---------------------
# AUTH ENDPOINTS
# ---------------------

@app.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


# ---------------------
# PROFILE ENDPOINTS
# ---------------------

@app.get("/profile", response_model=schemas.UserProfile)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/profile/update", response_model=schemas.UserOut)
def update_profile(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Re-fetch user in the current session
    db_user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.full_name:
        db_user.full_name = user_update.full_name
    if user_update.email:
        db_user.email = user_update.email
    if user_update.role:
        db_user.role = user_update.role

    db.commit()
    db.refresh(db_user)

    return schemas.UserOut.from_orm(db_user)


# ---------------------
# FARM ENDPOINTS
# ---------------------

@app.post("/farm/add", response_model=schemas.FarmResponse)
def add_farm(farm: schemas.FarmCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_farm = models.Farm(
        farm_name=farm.farm_name,
        location=farm.location,
        soil_type=farm.soil_type,
        area=farm.area,
        owner_id=current_user.id
    )
    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)
    return new_farm


@app.get("/farm/myfarms", response_model=list[schemas.FarmResponse])
def get_my_farms(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    farms = db.query(models.Farm).filter(models.Farm.owner_id == current_user.id).all()
    return farms


@app.put("/farm/update/{farm_id}", response_model=schemas.FarmResponse)
def update_farm(farm_id: int, farm: schemas.FarmCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_farm = db.query(models.Farm).filter(models.Farm.id == farm_id, models.Farm.owner_id == current_user.id).first()
    if not db_farm:
        raise HTTPException(status_code=404, detail="Farm not found or not authorized to update")

    db_farm.farm_name = farm.farm_name
    db_farm.location = farm.location
    db_farm.soil_type = farm.soil_type
    db_farm.area = farm.area

    db.commit()
    db.refresh(db_farm)
    return db_farm

@app.delete("/farm/delete/{farm_id}", status_code=204)
def delete_farm(farm_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Fetch the farm from the database
    farm = db.query(models.Farm).filter(models.Farm.id == farm_id).first()
    
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    # Optional: Only allow the owner or admin to delete
    if farm.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this farm")
    
    db.delete(farm)
    db.commit()
    
    return {"detail": "Farm deleted successfully"}


app.include_router(media_routes.router)