from fastapi import APIRouter
from database import *

router = APIRouter()


# db connection
connection, cursor = postgre_database_connection()


# registers new user
@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_new_user(new_user: CreateUser):
    return save_user_to_db(connection, cursor, new_user)


# login a user
@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(user_credentials: Login_user):
    return check_user_credentials(connection, cursor, user_credentials)
