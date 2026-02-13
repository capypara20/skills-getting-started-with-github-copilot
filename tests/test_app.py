import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Tennis Club" in data
    assert "participants" in data["Tennis Club"]

def test_signup_for_activity_success():
    email = "testuser@mergington.edu"
    activity = "Tennis Club"
    # Remove if already present
    client.delete(f"/activities/{activity}/signup?email={email}")
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert f"Signed up {email}" in response.json()["message"]
    # Clean up
    client.delete(f"/activities/{activity}/signup?email={email}")

def test_signup_for_activity_already_signed_up():
    email = "alex@mergington.edu"
    activity = "Tennis Club"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_for_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=someone@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_signup_for_activity_full():
    activity = "Debate Team"
    # Fill up the activity
    for i in range(12 - len(client.get("/activities").json()[activity]["participants"])):
        email = f"fulltest{i}@mergington.edu"
        client.post(f"/activities/{activity}/signup?email={email}")
    # Now try to add one more
    response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]
    # Clean up
    for i in range(12 - len(client.get("/activities").json()[activity]["participants"])):
        email = f"fulltest{i}@mergington.edu"
        client.delete(f"/activities/{activity}/signup?email={email}")

def test_delete_participant():
    email = "deleteuser@mergington.edu"
    activity = "Chess Club"
    # Ensure user is signed up
    client.post(f"/activities/{activity}/signup?email={email}")
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert f"Unregistered {email}" in response.json()["message"]
    # Try deleting again (should fail)
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]
