from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from backend.database.database import get_db
from backend.models.user import User
from backend.schemas.user import UserCreate, UserResponse, Token, UserProfileUpdate
from backend.utils.auth import get_password_hash, verify_password, create_access_token
from backend.utils.dependencies import get_current_user, get_current_admin

router = APIRouter(tags=["Authentication"])

VALID_ROLES = {"investor", "founder", "seeker", "collaborator", "member"}

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    role = user.role if user.role in VALID_ROLES else "member"
    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=get_password_hash(user.password),
        role=role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token(data={"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer", "user": new_user}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.password_hash or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "user": user}

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(updates: UserProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    for field, value in updates.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

# ── Admin-only stats endpoint ──────────────────────────────────────────────────
@router.get("/admin/stats")
def admin_stats(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    from backend.models.startup import Startup
    from backend.models.chat import ChatLog
    total_users    = db.query(User).count()
    total_startups = db.query(Startup).count()
    total_chats    = db.query(ChatLog).count()
    role_counts    = {}
    for role in ["investor", "founder", "seeker", "collaborator", "member"]:
        role_counts[role] = db.query(User).filter(User.role == role).count()
    return {
        "total_users": total_users,
        "total_startups": total_startups,
        "total_chats": total_chats,
        "role_breakdown": role_counts,
    }
