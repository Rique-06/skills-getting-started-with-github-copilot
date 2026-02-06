import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    yield
    # Reset activities after test
    activities.clear()
    activities.update({
        "Basketball": {
            "description": "Team sport focusing on basketball skills and competitive play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis techniques and participate in matches",
            "schedule": "Saturdays, 9:00 AM - 11:00 AM",
            "max_participants": 10,
            "participants": ["james@mergington.edu", "sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and musicals, develop acting skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucy@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and digital art techniques",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["ethan@mergington.edu", "mia@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })


def test_root_redirect():
    """Test that root endpoint redirects to static page"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_get_activities(reset_activities):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball" in data
    assert "Tennis Club" in data
    assert data["Basketball"]["description"] is not None
    assert isinstance(data["Basketball"]["participants"], list)


def test_signup_for_activity(reset_activities):
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Basketball/signup?email=newstudent@mergington.edu",
        method="POST"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in activities["Basketball"]["participants"]


def test_signup_duplicate(reset_activities):
    """Test that signing up twice fails"""
    client.post(
        "/activities/Basketball/signup?email=duplicate@mergington.edu",
        method="POST"
    )
    response = client.post(
        "/activities/Basketball/signup?email=duplicate@mergington.edu",
        method="POST"
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity(reset_activities):
    """Test signing up for a nonexistent activity"""
    response = client.post(
        "/activities/FakeActivity/signup?email=student@mergington.edu",
        method="POST"
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_unregister_from_activity(reset_activities):
    """Test unregistering from an activity"""
    # First sign up
    client.post(
        "/activities/Basketball/signup?email=unreg@mergington.edu",
        method="POST"
    )
    assert "unreg@mergington.edu" in activities["Basketball"]["participants"]
    
    # Then unregister
    response = client.delete(
        "/activities/Basketball/unregister?email=unreg@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "unreg@mergington.edu" not in activities["Basketball"]["participants"]


def test_unregister_not_signed_up(reset_activities):
    """Test unregistering when not signed up"""
    response = client.delete(
        "/activities/Basketball/unregister?email=notstudent@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"].lower()


def test_unregister_nonexistent_activity(reset_activities):
    """Test unregistering from a nonexistent activity"""
    response = client.delete(
        "/activities/FakeActivity/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_activities_structure(reset_activities):
    """Test that activities have the correct structure"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)
