import pytest
from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


class TestActivitiesEndpoints:
    """Test suite for activities endpoints"""

    def test_get_root_redirect(self):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_structure(self):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert "instructor" in chess_club
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_signup_new_participant(self):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_duplicate_participant(self):
        """Test signing up a participant who is already registered"""
        # Michael is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_activities(self):
        """Test that a student can sign up for multiple activities"""
        email = "multistudent@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify both registrations
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]

    def test_unregister_participant(self):
        """Test unregistering a participant"""
        email = "unregister_test@mergington.edu"
        
        # First, sign up the student
        client.post(f"/activities/Tennis Club/signup?email={email}")
        
        # Verify they're registered
        activities = client.get("/activities").json()
        assert email in activities["Tennis Club"]["participants"]
        
        # Now unregister
        response = client.delete(
            f"/activities/Tennis Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        
        # Verify they're unregistered
        activities = client.get("/activities").json()
        assert email not in activities["Tennis Club"]["participants"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from a nonexistent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_nonexistent_participant(self):
        """Test unregistering a participant who isn't registered"""
        response = client.delete(
            "/activities/Digital Art/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]

    def test_activity_capacity(self):
        """Test that activity capacity data is correct"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        expected_capacity = chess_club["max_participants"] - len(chess_club["participants"])
        assert expected_capacity >= 0

    def test_all_activities_exist(self):
        """Test that all expected activities are present"""
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Digital Art",
            "Music Band",
            "Robotics Club",
            "Debate Team"
        ]
        
        response = client.get("/activities")
        activities = response.json()
        
        for activity in expected_activities:
            assert activity in activities
