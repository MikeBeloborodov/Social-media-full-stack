from ctypes import util
import secrets
import pytest
from backend.main import app
from fastapi.testclient import TestClient
from backend.routers.logic import schemas
import utils


client = TestClient(app)


# tokens for test users
tokens = []

# created posts id's
created_posts_id = []

#constant for amount of users created
USERS_AMOUNT = 5


# check client type
def test_client_posts():
    assert type(client) == TestClient


# create and login ten users for tests
@pytest.mark.parametrize("login, password",
                        [(f"admin{a}@mail.com", f"admin{a}") for a in range(USERS_AMOUNT)])
def test_create_login_users(login, password):
    res = client.post("/register/", json={"email": login, "password": password})
    assert res.status_code == 201
    login_res = client.post("/login/", data={"username": login, "password": password})
    assert login_res.status_code == 200
    login_info = schemas.Token(**login_res.json())
    tokens.append(login_info.access_token)


# test posting posts from different users
@pytest.mark.parametrize("index",[a for a in range(USERS_AMOUNT)])
def test_post_new_posts(index):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {tokens[index]}"}
    res = client.post("/posts/", json={"title": f"test{index}", "content": f"test{index}"})
    new_post = schemas.ResponseNewPost(**res.json())
    assert new_post.title == f"test{index}"
    assert new_post.content == f"test{index}"
    assert new_post.likes == 0
    created_posts_id.append(new_post.id)


# test getting all posts from different users
@pytest.mark.parametrize("index",[a for a in range(USERS_AMOUNT)])
def test_get_all_posts(index):
    res = client.get("/posts/")
    test_post_from_db = utils.retrieve_post()
    if not test_post_from_db:
        assert res.status_code == 404
    else:
        assert res.status_code == 200


# test getting posts by id from different users
@pytest.mark.parametrize("index",[a for a in range(USERS_AMOUNT)])
def test_get_post_by_id(index):
    res = client.get(f"/posts/{created_posts_id[index]}")
    test_post_from_db = utils.retrieve_post_by_id(created_posts_id[index])
    
    post_by_id = schemas.Post(**res.json())
    
    # check if there is a post
    assert test_post_from_db

    # check paremeters
    assert post_by_id.id == test_post_from_db.id
    assert post_by_id.title == test_post_from_db.title
    assert post_by_id.content == test_post_from_db.content
    assert post_by_id.owner_id == test_post_from_db.owner_id
    assert post_by_id.likes == test_post_from_db.likes
    

# test updating posts from different users
@pytest.mark.parametrize("index",[a for a in range(USERS_AMOUNT)])
def test_updating_posts(index):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {tokens[index]}"}
    res = client.patch(f"/posts/{created_posts_id[index]}", json={"title": f"test update{index}", 
                                                "content": f"test update{index}"})
    assert res.status_code == 201
    updated_post = schemas.ResponseNewPost(**res.json())
    assert updated_post.title == f"test update{index}"
    assert updated_post.content == f"test update{index}"
    assert updated_post.likes == 0

# test liking posts from different users
@pytest.mark.parametrize("index",[a for a in range(USERS_AMOUNT)])
def test_liking_posts(index):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {tokens[index]}"}
    res = client.patch(f"/posts/like/{created_posts_id[index]}")
    assert res.status_code == 201
    liked_post = schemas.ResponseNewPost(**res.json())
    assert liked_post.likes == 1

    # test liking second time should return 403
    res = client.patch(f"/posts/like/{created_posts_id[index]}")
    assert res.status_code == 403


# test liking other people's posts 
@pytest.mark.parametrize("index",[a for a in range(USERS_AMOUNT - 1)])
def test_liking_other_posts(index):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {tokens[index]}"}
    res = client.patch(f"/posts/like/{created_posts_id[index + 1]}")
    assert res.status_code == 201
    liked_post = schemas.ResponseNewPost(**res.json())
    assert liked_post.likes == 2

    # test liking second time should return 403
    res = client.patch(f"/posts/like/{created_posts_id[index + 1]}")
    assert res.status_code == 403


# test deleting other people's posts 
@pytest.mark.parametrize("index",[a for a in range(USERS_AMOUNT - 1)])
def test_deleting_other_posts(index):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {tokens[0]}"}
    res = client.delete(f"/posts/{created_posts_id[index + 1]}")
    assert res.status_code == 403
    

# test deleting own posts 
@pytest.mark.parametrize("index",[a for a in range(USERS_AMOUNT)])
def test_deleting_own_posts(index):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {tokens[index]}"}
    deleted_post_from_db = utils.retrieve_post_by_id(created_posts_id[index])
    res = client.delete(f"/posts/{created_posts_id[index]}")
    assert res.status_code == 200
    deleted_post = schemas.Post(**res.json())
    
    assert deleted_post.id == deleted_post_from_db.id
    assert deleted_post.title == deleted_post_from_db.title
    assert deleted_post.content == deleted_post_from_db.content
    assert deleted_post.owner_id == deleted_post_from_db.owner_id
    assert deleted_post.likes == deleted_post_from_db.likes


@pytest.mark.parametrize("login, password",
                        [(f"admin{a}@mail.com", f"admin{a}") for a in range(USERS_AMOUNT)])
def test_deleting_users(login, password):
    utils.delete_test_user(login)
