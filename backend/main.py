from fastapi import FastAPI 
import routers.posts as posts
import routers.users as users
from fastapi.middleware.cors import CORSMiddleware

# sqalchemy creates tables
# models.Base.metadata.create_all(bind=engine)
# we will use alembic from now on


# app entry point
app = FastAPI()


# if you want only specific servers to be able to talk to your api
# put them in origins, otherwise use "*" to allow everyone
# origins = ["http://www.google.com"]
origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# main page
@app.get("/")
def send_index_page():
    return {"Message": "go to /docs to see api functionality"}


# router for posts
app.include_router(posts.router)


# router for users
app.include_router(users.router)
