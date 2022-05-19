from backend.main import app
from fastapi.testclient import TestClient
from database import override_get_db, engine, Test_environment
from backend.routers.logic.database import get_db, Base


if Test_environment:
    # creates test database if it doesn't exist
    Base.metadata.create_all(bind=engine)

    # override_get_db function to run tests on test database
    app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


# check client type
def test_client_root():
    assert type(client) == TestClient


# test status code 
def test_status():
    res = client.get("/")
    assert res.status_code == 200


# test response
def test_response():
    res = client.get("/").json().get("Message")
    assert res == "go to /docs to see api functionality"


