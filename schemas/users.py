from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = "unknown"
    bio: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None