from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app import models, schemas, utils, database
from app.utils.security import create_access_token, verify_password

router = APIRouter()

@router.post("/login")
async def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    # Query the database to get the user by email
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    # Check if user exists and the password is correct
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If authentication is successful, create a JWT token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}
