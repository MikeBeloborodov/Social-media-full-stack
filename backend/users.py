from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import database as db
from schemas import *
import orm_database
import orm_functions


router = APIRouter(
    tags=["User interaction"]
)


# db connection
connection, cursor = db.postgres_database_connection()


# registers new user
@router.post("/register/", status_code=status.HTTP_201_CREATED)
def create_new_user(new_user: CreateUser,
                    db: Session = Depends(orm_database.get_db)):

    #return db.save_user_to_db(connection, cursor, new_user)
    return orm_functions.save_user_to_db(new_user, db)


# login a user
@router.post("/login/", status_code=status.HTTP_200_OK, response_model=Token)
def login_user(user_credentials: OAuth2PasswordRequestForm = Depends()):
    return db.check_user_credentials(connection, cursor, user_credentials)
