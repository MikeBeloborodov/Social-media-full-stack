import orm_models
from sqlalchemy.orm import Session
from models import *
from utils import time_stamp
from fastapi import HTTPException, status


def send_all_posts(db: Session, user_id: int) -> list:
    # execution check
    try:
        posts = db.query(orm_models.Post).all()
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT RETRIEVE DATA FROM DB: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve data from DB")

    # availability check
    if not posts:
        print(f"[{time_stamp()}][!] FAILED TO RETURN ALL POSTS FROM DB - NO POSTS AVAILABLE")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Posts database is empty")
    
    # if ok return all posts
    return posts


def send_post_by_id(id: int, user_id: int, db: Session) -> dict:
    # execution check
    try:
        post = db.query(orm_models.Post).filter(orm_models.Post.id == id).first()
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT RETRIEVE DATA FROM DB: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve data from DB")
    
    # availability check
    if not post:
        print(f"[{time_stamp()}][!] FAILED TO RETURN POST BY ID {id} FROM DB - NOT FOUND")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This post does not exist")
    
    #if ok return post by id
    return post


def save_new_post_to_db(new_post: NewPost, db: Session, user_id: int) -> dict:
    # execution check
    try:
        # ** will unpack this dict in key=value format
        post_to_save = orm_models.Post(**new_post.dict())
        db.add(post_to_save)
        db.commit()
        db.refresh(post_to_save)
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT CREATE NEW POST: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not write post to DB")
    
    # if ok return saved post
    return post_to_save


def save_updated_post_by_id(id: int, updated_post: UpdatedPost, db: Session, user_id: int):
    # execution check
    try:
        post = db.query(orm_models.Post).filter(orm_models.Post.id == id).first()
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT RETRIEVE DATA FROM DB: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve data from DB")
    
    # availability check
    if not post:
        print(f"[{time_stamp()}][!] FAILED TO UPDATE POST BY ID {id} FROM DB - NOT FOUND")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This post does not exist")

    # execute update
    try:
        db.query(orm_models.Post).filter(orm_models.Post.id == id).update(updated_post.dict())
        db.commit()
        db.refresh(post)
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT UPDATE POST: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update post in DB")
    
    # if ok return updated post
    return post

def save_post_like_to_db(id: int, db: Session, user_id: int) -> dict:
    # execution check
    try:
        post = db.query(orm_models.Post).filter(orm_models.Post.id == id).first()
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT FIND POST TO LIKE: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not find post to like in DB")
    
    # availability check
    if not post:
        print(f"[{time_stamp()}][!] USER ID {user_id} TRYING TO LIKE A NON EXISTING POST")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This post does not exist")
    
    # execute update
    try:
        db.query(orm_models.Post).filter(orm_models.Post.id == id).update({"likes": orm_models.Post.likes + 1})
        db.commit()
        db.refresh(post)
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT UPDATE POST: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update post in DB")
    
    # if ok return liked post
    return post


def delete_post_from_db(id: int, db: Session, user_id: int) -> dict:
    # execution check
    try:
        post = db.query(orm_models.Post).filter(orm_models.Post.id == id).first()
        db.query(orm_models.Post).filter(orm_models.Post.id == id).delete()
        db.commit()
    except Exception as execution_error:
        print(f"[{time_stamp()}][!] COULD NOT DELETE POST FROM DB: {execution_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete post from DB")
    
    # availability check
    if not post:
        print(f"[{time_stamp()}][!] FAILED TO DELETE POST BY ID {id} FROM DB - NOT FOUND")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This post does not exist")
    
    #if ok return deleted post
    return post
    