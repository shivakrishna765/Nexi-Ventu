from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.config.settings import settings
from backend.database.database import get_db
from backend.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_founder(current_user: User = Depends(get_current_user)):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Only founders can perform this action")
    return current_user

def get_current_investor(current_user: User = Depends(get_current_user)):
    if current_user.role != "investor":
        raise HTTPException(status_code=403, detail="Only investors can perform this action")
    return current_user

def get_current_admin(current_user: User = Depends(get_current_user)):
    """Blocks access unless the user has is_admin=True in the database."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
