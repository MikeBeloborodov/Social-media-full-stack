from locale import strcoll
from jose import JWTError, jwt
from datetime import datetime, timedelta
from settings import settings
from models import *
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.access_token_expire_minutes)
now = datetime.now()
time_string = now.strftime("%H:%M:%S %Y-%m-%d")


def create_access_token(data: dict) -> str:
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        print(to_encode)

        # payload, secret key, algorithm
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt
    except JWTError as error:
        print(f"[{time_string}][!!] CREATE ACCESS TOKEN ERROR: {error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token creation error")


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

        # validate id with pydantic
        token_data = TokenData(id=user_id)  
    except JWTError as error:
        print(f"[{time_string}][!!] VERIFY ACCESS TOKEN ERROR: {error}")
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate" : "Bearer"})

    return verify_access_token(token, credentials_exception)
