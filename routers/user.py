from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.user import UserOut
from schemas.schema import User
from database import get_db
from utils.dependencies import auth_middleware


user_router = APIRouter(prefix="/user", tags=["User"], dependencies=[Depends(auth_middleware)])

@user_router.get("/{userid}", response_model=UserOut)
def get_user(userid: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userid == userid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user