from sqlalchemy.orm import Session
from backend.routers.logic.database import engine
from backend.routers.logic import models

def delete_test_user(email: str = 'admin@mail.com'):
    with Session(engine) as session:
        session.query(models.User).filter(models.User.email == email).delete()
        session.commit()

def get_test_user(email: str = 'admin@mail.com'):
    with Session(engine) as session:
        user = session.query(models.User).filter(models.User.email == email).first()
        return user

def retrieve_post():
    with Session(engine) as session:
        post = session.query(models.Post).first()
        return post

def retrieve_post_by_id(id: str):
    with Session(engine) as session:
        post = session.query(models.Post).filter(models.Post.id == id).first()
        return post