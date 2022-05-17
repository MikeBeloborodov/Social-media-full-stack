from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import datetime


class Post(BaseModel):
    id: int
    owner_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    likes: int
    
    class Config:
        orm_mode = True

class NewPost(BaseModel):
    title: str
    content: str


class ResponseNewPost(BaseModel):
    id: int
    owner_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    likes: int

    class Config:
        orm_mode = True


class UpdatedPost(BaseModel):
    title: str
    content: str


class ResponseUpdatedPost(BaseModel):
    id: int
    owner_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    likes: int

    class Config:
        orm_mode = True


class CreateUser(BaseModel):
    email: EmailStr
    password: str


class ResponseCreateUser(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    date_time: str


class TokenData(BaseModel):
    id: Optional[str] = None