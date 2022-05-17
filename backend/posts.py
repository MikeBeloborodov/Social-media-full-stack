from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from schemas import *
import database
import oauth2
import orm_database
import orm_functions


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


# db connection
connection, cursor = database.postgres_database_connection()


# sends all posts
@router.get("/", status_code=status.HTTP_200_OK)
def send_all_posts(db: Session = Depends(orm_database.get_db),
                    user_id: int = Depends(oauth2.get_current_user)):
    
    return orm_functions.send_all_posts(db, user_id)


# sends post by id
@router.get("/{id}", status_code=status.HTTP_200_OK)
def send_post_by_id(id: int, 
                    user_id: int = Depends(oauth2.get_current_user),
                    db: Session = Depends(orm_database.get_db)):

   return orm_functions.send_post_by_id(id, user_id, db)


# creates new post
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_new_post(new_post: NewPost,
                    db: Session = Depends(orm_database.get_db), 
                    user_id: int = Depends(oauth2.get_current_user)):
    
    return orm_functions.save_new_post_to_db(new_post, db, user_id)


# updates post by id
@router.patch("/{id}", status_code=status.HTTP_201_CREATED)
def update_post_by_id(id: int, 
                    updated_post: UpdatedPost, 
                    db: Session = Depends(orm_database.get_db),
                    user_id: int = Depends(oauth2.get_current_user)):

    return orm_functions.save_updated_post_by_id(id, updated_post, db, user_id)


# likes a post
@router.patch("/like/{id}", status_code=status.HTTP_201_CREATED)
def like_post_by_id(id: int, 
                    db: Session = Depends(orm_database.get_db),
                    user_id: int = Depends(oauth2.get_current_user)):

    return orm_functions.save_post_like_to_db(id, db, user_id)


# deletes post by id
@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_post_by_id(id: int, 
                    db: Session = Depends(orm_database.get_db),
                    user_id: int = Depends(oauth2.get_current_user)):

    return orm_functions.delete_post_from_db(id, db, user_id)
