import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in {302, 307}
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_data():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_adds_participant():
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant():
    email = activities["Chess Club"]["participants"][0]
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant():
    email = activities["Chess Club"]["participants"][0]
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant():
    email = "missing@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
