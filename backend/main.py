from fastapi import FastAPI
from database import *
import posts
import users

app = FastAPI()


@app.get("/")
def send_index_page():
    return {"Message": "go to /docs to see api functionality"}


# db connection
connection, cursor = postgre_database_connection()


# router for posts
app.include_router(posts.router)


# router for users
app.include_router(users.router)
