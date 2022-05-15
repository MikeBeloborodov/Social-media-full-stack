from fastapi import FastAPI
from database import *
from models import *

app = FastAPI()

# db connection
connection, cursor = postgre_database_connection()

@app.get("/")
def send_index_page():
	return {"Message" : "Front page"}

# sends all posts
@app.get("/posts")
def send_all_posts():
	return return_all_posts(connection, cursor)

# sends post by id
@app.get("/posts/{id}")
def send_post_by_id(id: str):
	return return_post_by_id(connection, cursor, id)

# creates new post
@app.post("/posts")
def create_new_post(new_post: Post):
	return save_post_to_db(connection, cursor, new_post)

# updates post by id
@app.patch("/posts/{id}")
def update_post_by_id(updated_post: Post):
	return update_post_in_db(connection, cursor, updated_post)

# registers new user
@app.post("/register")
def create_new_user(new_user: User):
	return save_user_to_db(connection, cursor, new_user)