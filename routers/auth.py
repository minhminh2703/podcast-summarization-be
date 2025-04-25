# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.user import UserCreate, UserLogin, UserOut
from schemas.schema import User
from service.auth_service import get_password_hash, verify_password, create_access_token
from database import get_db
from email_validator import validate_email, EmailNotValidError

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/signup", response_model=UserOut)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Validate email format
    try:
        valid = validate_email(user_data.email)
    except EmailNotValidError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email address"
        )
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == valid.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    # Create user
    new_user = User(
        email=valid.email,
        password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@auth_router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials."
        )
    # Credentials valid, create JWT
    access_token = create_access_token(data={"userid": user.userid})
    return {"access_token": access_token, "token_type": "bearer", "userid": user.userid}





