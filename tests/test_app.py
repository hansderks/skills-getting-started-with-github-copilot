import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

# fixture to reset activities between tests
@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # should have some known keys
    assert "Chess Club" in data


def test_signup_success():
    email = "test@school.edu"
    resp = client.post(f"/activities/Chess Club/signup?email={email}")
    assert resp.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate():
    email = "dup@school.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    resp = client.post(f"/activities/Chess Club/signup?email={email}")
    assert resp.status_code == 400


def test_signup_unknown_activity():
    resp = client.post("/activities/NoSuch/signup?email=fake@school.edu")
    assert resp.status_code == 404


def test_remove_signup_success():
    email = "remove@school.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    resp = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert resp.status_code == 200
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_remove_signup_not_found():
    resp = client.delete("/activities/Chess Club/signup?email=missing@school.edu")
    assert resp.status_code == 404


def test_root_redirect():
    # TestClient uses follow_redirects instead of allow_redirects
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (307, 302)
    assert resp.headers.get("location") == "/static/index.html"
