# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    profile_picture: Optional[str] = None


class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    userid: UUID

    class Config:
        from_attribute = True
