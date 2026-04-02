from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.models.startup import Startup
from backend.models.user import User
from backend.schemas.startup import StartupCreate, StartupUpdate, StartupResponse
from backend.utils.dependencies import get_current_user, get_current_founder

router = APIRouter(tags=["Startups"])

@router.post("/add-startup", response_model=StartupResponse, status_code=status.HTTP_201_CREATED)
def add_startup(startup: StartupCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_founder)):
    new_startup = Startup(**startup.model_dump(), created_by=current_user.id)
    db.add(new_startup)
    db.commit()
    db.refresh(new_startup)
    return new_startup

@router.get("/get-startups", response_model=List[StartupResponse])
def get_startups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    startups = db.query(Startup).offset(skip).limit(limit).all()
    return startups

@router.get("/startup/{id}", response_model=StartupResponse)
def get_startup(id: int, db: Session = Depends(get_db)):
    startup = db.query(Startup).filter(Startup.id == id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    return startup

@router.put("/update-startup/{id}", response_model=StartupResponse)
def update_startup(id: int, startup_update: StartupUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    startup = db.query(Startup).filter(Startup.id == id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    if startup.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this startup")
        
    for key, value in startup_update.model_dump(exclude_unset=True).items():
        setattr(startup, key, value)
    
    db.commit()
    db.refresh(startup)
    return startup

@router.delete("/startup/{id}")
def delete_startup(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    startup = db.query(Startup).filter(Startup.id == id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Startup not found")
    if startup.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this startup")
        
    db.delete(startup)
    db.commit()
    return {"detail": "Startup deleted successfully"}
