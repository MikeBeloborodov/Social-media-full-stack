from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
import database as db
from models import *

router = APIRouter(
    tags=["User interaction"]
)


# db connection
connection, cursor = db.postgres_database_connection()


# registers new user
@router.post("/register/", status_code=status.HTTP_201_CREATED)
def create_new_user(new_user: CreateUser):
    return db.save_user_to_db(connection, cursor, new_user)


# login a user
@router.post("/login/", status_code=status.HTTP_200_OK, response_model=Token)
def login_user(user_credentials: OAuth2PasswordRequestForm = Depends()):
    return db.check_user_credentials(connection, cursor, user_credentials)
