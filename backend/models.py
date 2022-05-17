from pydantic import BaseModel, EmailStr
from typing import Optional


class User(BaseModel):
    email: EmailStr
    password: str


class NewPost(BaseModel):
    title: str
    content: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class CreateUser(BaseModel):
    email: EmailStr
    password: str


class UpdateUser(BaseModel):
    email: EmailStr


class UpdatedPost(BaseModel):
    title: str
    content: str


class Token(BaseModel):
    access_token: str
    token_type: str
    date_time: str


class TokenData(BaseModel):
    id: Optional[str] = None