from pydantic import BaseModel

class User(BaseModel):
    name: str
    email:str
    password: str

class Post(BaseModel):
    title: str
    content: str
    owner_email: str

class Login_user(BaseModel):
    email: str
    password: str