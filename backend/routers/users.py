from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .logic import schemas
from .logic import database
from .logic import functions


router = APIRouter(
    tags=["User interaction"]
)


# registers new user
@router.post("/register/", status_code=status.HTTP_201_CREATED, response_model=schemas.ResponseCreateUser)
def create_new_user(new_user: schemas.CreateUser,
                    db: Session = Depends(database.get_db)):

    return functions.save_user_to_db(new_user, db)


# login a user
@router.post("/login/", status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login_user(user_credentials: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(database.get_db)):

    #return db.check_user_credentials(connection, cursor, user_credentials)
    return functions.login_check_credentials(user_credentials, db)
