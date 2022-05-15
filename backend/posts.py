from fastapi import APIRouter
import models
from database import *


router = APIRouter()


# db connection
connection, cursor = postgre_database_connection()


# sends all posts
@router.get("/posts", status_code=status.HTTP_200_OK)
def send_all_posts():
    return return_all_posts(connection, cursor)


# sends post by id
@router.get("/posts/{id}", status_code=status.HTTP_200_OK)
def send_post_by_id(id: int):
    return return_post_by_id(connection, cursor, id)


# creates new post
@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_new_post(new_post: models.Post):
    return save_post_to_db(connection, cursor, new_post)


# updates post by id
@router.patch("/posts/{id}", status_code=status.HTTP_201_CREATED)
def update_post_by_id(id: int, updated_post: models.Post, user: models.User):
    return update_post_in_db(connection, cursor, id, updated_post, user)


# likes a post
@router.patch("/posts/like/{id}", status_code=status.HTTP_201_CREATED)
def like_post_by_id(id: int, user_email: str):
    return save_user_like(connection, cursor, id, user_email)


# deletes post by id
@router.delete("/posts/{id}", status_code=status.HTTP_200_OK)
def delete_post_by_id(id: int, user: models.User):
    return delete_post_from_db(connection, cursor, id, user)
