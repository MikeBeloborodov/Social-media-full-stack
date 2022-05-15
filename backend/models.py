from pydantic import BaseModel

class User(BaseModel):
    name: str
    email:str

class Post(BaseModel):
    title: str
    content: str
    owner_email: str
