# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas.user import UserCreate, UserLogin, UserOut
from models.user import User
from utils.security import get_password_hash, verify_password, create_access_token
from database import get_db

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/signup", response_model=UserOut)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    # Create user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user  

@auth_router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found"
        )
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )
    # Credentials valid, create JWT
    access_token = create_access_token(data={"user_id": user.user_id})
    return {"access_token": access_token, "token_type": "bearer"}
