"""
FastAPI backend tests for the Mergington High School Activities API.
Tests are structured using the Arrange-Act-Assert (AAA) pattern.
"""

from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


# ============================================================================
# GET /activities endpoint tests
# ============================================================================

def test_get_activities_returns_all_activities():
    """Test that GET /activities returns all activities with correct structure."""
    # Arrange
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Art Studio",
        "Music Band",
        "Debate Club",
        "Science Club",
    ]
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities = response.json()
    
    # Verify all expected activities are present
    for activity_name in expected_activities:
        assert activity_name in activities
    
    # Verify each activity has required fields
    for activity_name, activity_data in activities.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_get_activities_contains_existing_participants():
    """Test that participants list for an activity shows existing participants."""
    # Arrange
    activity_name = "Chess Club"
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    activities = response.json()
    chess_club = activities[activity_name]
    
    # Verify Chess Club has participants
    assert len(chess_club["participants"]) > 0
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


# ============================================================================
# POST /activities/{activity_name}/signup endpoint tests
# ============================================================================

def test_signup_for_activity_success():
    """Test successful signup for an activity."""
    # Arrange
    activity_name = "Art Studio"
    new_email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert new_email in result["message"]
    assert activity_name in result["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert new_email in activities[activity_name]["participants"]


def test_signup_for_non_existent_activity_returns_404():
    """Test that signing up for a non-existent activity returns 404."""
    # Arrange
    fake_activity = "Non Existent Activity"
    email = "test@mergington.edu"
    
    # Act
    response = client.post(
        f"/activities/{fake_activity}/signup",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_signup_duplicate_student_returns_400():
    """Test that signing up the same student twice returns 400."""
    # Arrange
    activity_name = "Tennis Club"
    existing_email = "sarah@mergington.edu"
    
    # Act - First signup should succeed
    response_first = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email}
    )
    
    # Assert first signup
    assert response_first.status_code == 400
    result_first = response_first.json()
    assert "detail" in result_first
    assert "already signed up" in result_first["detail"].lower()


# ============================================================================
# DELETE /activities/{activity_name}/unregister endpoint tests
# ============================================================================

def test_unregister_from_activity_success():
    """Test successful unregistration from an activity."""
    # Arrange
    activity_name = "Music Band"
    email_to_remove = "noah@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email_to_remove}
    )
    
    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email_to_remove in result["message"]
    assert activity_name in result["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email_to_remove not in activities[activity_name]["participants"]


def test_unregister_from_non_existent_activity_returns_404():
    """Test that unregistering from a non-existent activity returns 404."""
    # Arrange
    fake_activity = "Non Existent Activity"
    email = "test@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{fake_activity}/unregister",
        params={"email": email}
    )
    
    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_unregister_student_not_registered_returns_400():
    """Test that unregistering a student not in the activity returns 400."""
    # Arrange
    activity_name = "Debate Club"
    unregistered_email = "notregistered@mergington.edu"
    
    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": unregistered_email}
    )
    
    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "not registered" in result["detail"].lower()
