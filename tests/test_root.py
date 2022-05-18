from backend.main import app
from fastapi.testclient import TestClient


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


