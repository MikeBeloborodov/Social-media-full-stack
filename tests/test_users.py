from backend.main import app
from fastapi.testclient import TestClient
from backend.routers.logic import schemas
import utils
import pytest
from database import override_get_db, engine, Test_environment
from backend.routers.logic.database import get_db, Base


if Test_environment:
    # creates test database if it doesn't exist
    Base.metadata.create_all(bind=engine)

    # override_get_db function to run tests on test database
    app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)

#constant for amount of users created
USERS_AMOUNT = 5


# check client type
def test_client_users():
    assert type(client) == TestClient


# check status code
def test_status():
    res = client.post("/register/", json={"email": "admin@mail.com", "password": "admin"})
    utils.delete_test_user()
    assert res.status_code == 201


# test response object on register
def test_response_register():
    res = client.post("/register/", json={"email": "admin@mail.com", "password": "admin"})
    utils.delete_test_user()
    new_user = schemas.ResponseCreateUser(**res.json())
    assert new_user.email == "admin@mail.com"


# test to prevent users with the same email
def test_double_creation():
    res = client.post("/register/", json={"email": "admin@mail.com", "password": "admin"})
    res = client.post("/register/", json={"email": "admin@mail.com", "password": "admin"})
    utils.delete_test_user()
    assert res.json().get("detail") == "Error. This user already exists."
    assert res.status_code == 403


# test creating many users in a row
@pytest.mark.parametrize("login, password",[(f"admin{a}@mail.com", f"admin{a}") for a in range(USERS_AMOUNT)])
def test_create_users(login, password):
    res = client.post("/register/", json={"email": login, "password": password})
    utils.delete_test_user(login)
    assert res.status_code == 201


# test if response data and data in our database is the same
def test_created_user_profile():
    res = client.post("/register/", json={"email": "admin@mail.com", "password": "admin"})
    user = utils.get_test_user()
    utils.delete_test_user()
    assert user.id == res.json().get("id")
    assert user.email == res.json().get("email")
    assert str(user.created_at)[:10] == str(res.json().get("created_at"))[:10]


# test login status code
def test_login():
    res = client.post("/register/", json={"email": "admin@mail.com", "password": "admin"})
    assert res.status_code == 201
    login = client.post("/login/", data={"username": "admin@mail.com", "password": "admin"})
    utils.delete_test_user()
    assert login.status_code == 200


# test login resoponse data
def test_login_response():
    res = client.post("/register/", json={"email": "admin@mail.com", "password": "admin"})
    assert res.status_code == 201
    login = client.post("/login/", data={"username": "admin@mail.com", "password": "admin"})
    utils.delete_test_user()
    login_info = schemas.Token(**login.json())
    assert login_info.token_type == "bearer"


# test login many users at once
@pytest.mark.parametrize("login, password",[(f"admin{a}@mail.com", f"admin{a}") for a in range(USERS_AMOUNT)])
def test_login_users(login, password):
    res = client.post("/register/", json={"email": login, "password": password})
    assert res.status_code == 201
    login_res = client.post("/login/", data={"username": login, "password": password})
    utils.delete_test_user(login)
    login_info = schemas.Token(**login_res.json())