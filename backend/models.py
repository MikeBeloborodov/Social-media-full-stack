from pydantic import BaseModel, EmailStr


class User(BaseModel):
    email: EmailStr
    password: str


class Post(BaseModel):
    title: str
    content: str
    owner_email: EmailStr


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class CreateUser(BaseModel):
    email: EmailStr
    password: str
