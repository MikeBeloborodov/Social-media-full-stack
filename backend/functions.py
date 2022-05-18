import copy
import models
from sqlalchemy.orm import Session
from .schemas import *
from .utils import time_stamp
from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm
import oauth2
from typing import Optional
from sqlalchemy import or_


def retrieve_posts(db: Session, user_id: int, limit: int, skip: int, search: Optional[str]) -> list:
    # execution check
    try:
        posts = (db.query(models.Post)
                    .filter(or_(models.Post.content.contains(search), models.Post.title.contains(search)))
                    .order_by(models.Post.id)
                    .offset(skip)
                    .limit(limit)
                    .all())
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT RETRIEVE DATA FROM DB: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Could not retrieve data from DB")

    # availability check
    if not posts:
        print(f"[{time_stamp()}][!] FAILED TO RETURN ALL POSTS FROM DB - NO POSTS AVAILABLE")
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
                                    detail="Posts database is empty")
    
    # if ok return all posts
    return posts


def retrieve_post_by_id(id: int, user_id: int, db: Session) -> dict:
    # execution check
    try:
        post = db.query(models.Post).filter(models.Post.id == id).first()
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT RETRIEVE DATA FROM DB: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Could not retrieve data from DB")
    
    # availability check
    if not post:
        print(f"[{time_stamp()}][!] FAILED TO RETURN POST BY ID {id} FROM DB - NOT FOUND")
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
                                    detail="This post does not exist")
    
    #if ok return post by id
    return post


def save_new_post_to_db(new_post: NewPost, db: Session, user_id: int) -> dict:
    # execution check
    try:
        # ** will unpack this dict in key=value format
        post_to_save = models.Post(**new_post.dict(), owner_id=user_id)
        db.add(post_to_save)
        db.commit()
        db.refresh(post_to_save)
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT CREATE NEW POST: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Could not write post to DB")
    
    # if ok return saved post
    return post_to_save


def save_updated_post_by_id(id: int, updated_post: UpdatedPost, db: Session, user_id: int):
    # execution check
    try:
        post_query = db.query(models.Post).filter(models.Post.id == id)
        post = post_query.first()
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT RETRIEVE DATA FROM DB: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Could not retrieve data from DB")
    
    # availability check
    if not post:
        print(f"[{time_stamp()}][!] FAILED TO UPDATE POST BY ID {id} FROM DB - NOT FOUND")
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
                                    detail="This post does not exist")

    # access check
    if post.owner_id != user_id:
        print(f"[{time_stamp()}][!] VALIDATION ERROR FROM USER ID {user_id} TO UPDATE POST")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong credentials")

    # execute update
    try:
        final_update = updated_post.dict()
        final_update['updated_at'] = datetime.now()
        post_query.update(final_update, synchronize_session=False)
        db.commit()
        db.refresh(post)
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT UPDATE POST: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Could not update post in DB")
    
    # if ok return updated post
    return post

def save_post_like_to_db(id: int, db: Session, user_id: int) -> dict:
    # execution check
    try:
        post_query = db.query(models.Post).filter(models.Post.id == id)
        post = post_query.first()
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT FIND POST TO LIKE: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Could not find post to like in DB")
    
    # availability check
    if not post:
        print(f"[{time_stamp()}][!] USER ID {user_id} TRYING TO LIKE A NON EXISTING POST")
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
                                    detail="This post does not exist")
    
    # double like check
    try:
        already_liked = (db.query(models.Like)
                        .filter(models.Like.post_id == post.id and models.Like.user_id == user_id)
                        .first())
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] ERROR DURING ACCESSING LIKE TABLE: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Database error")
    
    if already_liked:
        print(f"[{time_stamp()}][!] USER ID {user_id} TRYING TO LIKE A POST AGAIN")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User already liked this post")

    # execute update
    try:
        post_query.update({"likes": models.Post.likes + 1}, synchronize_session=False)
        db.commit()
        db.refresh(post)
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT UPDATE POST: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Could not update post in DB")
    
    # save like to the table
    try:
        db.add(models.Like(post_id=post.id, user_id=user_id))
        db.commit()
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT ADD LIKE TO A TABLE: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Could not add like in DB")

    # if ok return liked post
    return post


def delete_post_from_db(id: int, db: Session, user_id: int) -> dict:
    # execution check
    try:
        post_query = db.query(models.Post).filter(models.Post.id == id)
        post = copy.deepcopy(post_query.first())
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT EXTRACT POST FROM DB TO DELETE: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Could not extract post from DB")
    
    # availability check
    if not post:
        print(f"[{time_stamp()}][!] FAILED TO DELETE POST BY ID {id} FROM DB - NOT FOUND")
        raise HTTPException(status.HTTP_404_NOT_FOUND, 
                                    detail="This post does not exist")
    
    # access check
    if post.owner_id != user_id:
        print(f"[{time_stamp()}][!] VALIDATION ERROR FROM USER ID {user_id} TO DELETE POST")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong credentials")

    # execute delete post
    try:
        post_query.delete(synchronize_session=False)
        db.commit()
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT DELETE POST FROM DB: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Could not delete post from DB")

    #if ok return deleted post
    return post
    

def save_user_to_db(new_user: CreateUser, db: Session ) ->dict:
     # hash password
    try:
        pwd_context = CryptContext(schemes=['bcrypt'])
        new_user.password = pwd_context.hash(new_user.password)
    except Exception as hash_error:
        print(f"[{time_stamp()}][!] UNABLE TO HASH NEW USER PASSWORD - {new_user.email}")
        print(f"[{time_stamp()}]Error: {hash_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user, internal error")

    # check if user already exists
    try:
        user_query = db.query(models.User).filter(models.User.email == new_user.email)
        found_user = user_query.first()
    except Exception as user_validation_error:
        print(f"[{time_stamp()}][!] ERROR DURING USER SEARCH IN DB - {new_user.email}")
        print(f"[{time_stamp()}]Error: {user_validation_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database internal error during user search")

    if found_user:
        print(f"[{time_stamp()}][!] ERROR, USER {new_user.email} ALREADY EXISTS!")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Error. This user already exists.")
    
    # execution check
    try:
        # ** will unpack this dict in key=value format
        user_to_save = models.User(**new_user.dict())
        db.add(user_to_save)
        db.commit()
        db.refresh(user_to_save)
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT CREATE NEW USER: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Could not save USER to DB")
    
    # if ok return saved user
    return user_to_save


def login_check_credentials(user_credentials: OAuth2PasswordRequestForm, db: Session):
    # retrieve user from db
    try:
        user_query = db.query(models.User).filter(models.User.email == user_credentials.username)
        found_user = user_query.first()
    except Exception as user_validation_error:
        print(f"[{time_stamp()}][!] ERROR DURING USER SEARCH IN DB - {user_credentials.username}")
        print(f"[{time_stamp()}]Error: {user_validation_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database internal error during user search")

    if not found_user:
        print(f"[{time_stamp()}][!] VALIDATION ERROR FROM USER {user_credentials.username} TO LOGIN, EMAIL IS WRONG")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong credentials")
    
    # then we check if stored hashed password and given password are the same
    pwd_context = CryptContext(schemes=['bcrypt'])
    if not pwd_context.verify(user_credentials.password, found_user.password):
        print(f"[{time_stamp()}][!] USER {user_credentials.username} TRYING TO LOGIN WITH A WRONG PASSWORD")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong credentials")

    # if everything is okay we send data back
    print(f"[{time_stamp()}][+] USER {user_credentials.username} IS NOW LOGGED IN")
    access_token = oauth2.create_access_token(data = {"user_id" : found_user.id})

    return {"access_token": access_token, "token_type": "bearer", "date_time" : time_stamp()}