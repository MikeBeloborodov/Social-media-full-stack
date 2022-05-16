from fastapi import APIRouter, status, Depends
import models
import database as db
import oauth2


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


# db connection
connection, cursor = db.postgres_database_connection()


# sends all posts
@router.get("/", status_code=status.HTTP_200_OK)
def send_all_posts():
    return db.return_all_posts(connection, cursor)


# sends post by id
@router.get("/{id}", status_code=status.HTTP_200_OK)
def send_post_by_id(id: int):
    return db.return_post_by_id(connection, cursor, id)


# creates new post
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_new_post(new_post: models.Post, user_id: int = Depends(oauth2.get_current_user)):
    return db.save_post_to_db(connection, cursor, new_post)


# updates post by id
@router.patch("/{id}", status_code=status.HTTP_201_CREATED)
def update_post_by_id(id: int, updated_post: models.UpdatedPost, user_id: int = Depends(oauth2.get_current_user)):
    return db.save_updated_post_by_id(connection, cursor, id, updated_post, user_id)


# likes a post
@router.patch("/like/{id}", status_code=status.HTTP_201_CREATED)
def like_post_by_id(id: int, user_id: int = Depends(oauth2.get_current_user)):
    return db.save_user_like(connection, cursor, id, user_id)


# deletes post by id
@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_post_by_id(id: int, user_id: int = Depends(oauth2.get_current_user)):
    return db.delete_post_from_db(connection, cursor, id, user_id)
