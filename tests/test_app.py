"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a test client
client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a clean state before each test"""
    original_activities = {
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
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test cases for GET /activities endpoint"""
    
    def test_get_activities_returns_dict(self, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activity_has_required_fields(self, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignup:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        data = response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, reset_activities):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 404
    
    def test_signup_duplicate_email(self, reset_activities):
        """Test signup with email already registered for activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_increments_participant_count(self, reset_activities):
        """Test that signup adds participant to the activity"""
        initial_count = len(activities["Chess Club"]["participants"])
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        assert len(activities["Chess Club"]["participants"]) == initial_count + 1


class TestUnregister:
    """Test cases for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, reset_activities):
        """Test successful unregister from an activity"""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, reset_activities):
        """Test unregister from an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 404
    
    def test_unregister_not_registered(self, reset_activities):
        """Test unregister for email not registered for activity"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_decrements_participant_count(self, reset_activities):
        """Test that unregister removes participant from the activity"""
        initial_count = len(activities["Chess Club"]["participants"])
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        assert len(activities["Chess Club"]["participants"]) == initial_count - 1


class TestRoot:
    """Test cases for GET / endpoint"""
    
    def test_root_redirects_to_static(self, reset_activities):
        """Test that root path redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
