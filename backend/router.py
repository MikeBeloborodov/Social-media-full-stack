from fastapi import FastAPI
from database import *
from models import *

app = FastAPI()

# db connection
connection, cursor = postgre_database_connection()

@app.get("/")
def send_index_page():
	return {"Message" : "go to /docs to see api functionality"}

# sends all posts
@app.get("/posts")
def send_all_posts():
	return return_all_posts(connection, cursor)

# sends post by id
@app.get("/posts/{id}")
def send_post_by_id(id: int):
	return return_post_by_id(connection, cursor, id)

# creates new post
@app.post("/posts")
def create_new_post(new_post: Post):
	return save_post_to_db(connection, cursor, new_post)

# updates post by id
@app.patch("/posts/{id}")
def update_post_by_id(id: int, updated_post: Post, user: User):
	return update_post_in_db(connection, cursor, id, updated_post, user)

# likes a post
@app.patch("/posts/like/{id}")
def like_post_by_id(id: int, user_email: str):
	return save_user_like(connection, cursor, id, user_email)

#deletes post by id
@app.delete("/posts/{id}")
def delete_post_by_id(id: int, user: User):
	return delete_post_from_db(connection, cursor, id, user)

# registers new user
@app.post("/register")
def create_new_user(new_user: User):
	return save_user_to_db(connection, cursor, new_user)

# login a user
@app.post("/login")
def login_user(user_credentials: Login_user):
	return check_user_credentials(connection, cursor, user_credentials)