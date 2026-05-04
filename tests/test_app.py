"""
Pytest test suite for the Mergington High School FastAPI app.

Tests use the Arrange-Act-Assert pattern and reset in-memory state before each test.
"""

import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_names = ["Chess Club", "Programming Class", "Gym Class"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    for name in expected_names:
        assert name in data
        assert "description" in data[name]
        assert "schedule" in data[name]
        assert "max_participants" in data[name]
        assert "participants" in data[name]


def test_signup_adds_student_to_activity(client):
    # Arrange
    activity = "Basketball Team"
    email = "new_student@mergington.edu"
    path = f"/activities/{quote(activity, safe='')}/signup"

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in client.get("/activities").json()[activity]["participants"]


def test_duplicate_signup_returns_400(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    path = f"/activities/{quote(activity, safe='')}/signup"

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]
    assert client.get("/activities").json()[activity]["participants"].count(email) == 1


def test_unregister_removes_student_from_activity(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    path = f"/activities/{quote(activity, safe='')}/signup"

    # Act
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"
    assert email not in client.get("/activities").json()[activity]["participants"]
