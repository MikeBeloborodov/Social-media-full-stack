from fastapi import FastAPI 
import posts
import users
from orm_database import engine
import orm_models


# sqalchemy creates tables
orm_models.Base.metadata.create_all(bind=engine)


# app entry point
app = FastAPI()


# main page
@app.get("/")
def send_index_page():
    return {"Message": "go to /docs to see api functionality"}


# router for posts
app.include_router(posts.router)


# router for users
app.include_router(users.router)
