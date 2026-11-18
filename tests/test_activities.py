"""
Tests for GET /activities endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestGetActivities:
    """Test suite for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all available activities.
        
        AAA Pattern:
        - Arrange: TestClient is ready (from fixture)
        - Act: Call GET /activities
        - Assert: Verify response contains all activities
        """
        # Arrange
        # (client fixture already set up)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        # Verify some expected activities exist
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_contains_correct_structure(self, client):
        """
        Test that each activity has the correct data structure.
        
        AAA Pattern:
        - Arrange: TestClient is ready
        - Act: Call GET /activities
        - Assert: Verify each activity has required fields
        """
        # Arrange
        # (client fixture already set up)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants_are_emails(self, client):
        """
        Test that participants in activities are email strings.
        
        AAA Pattern:
        - Arrange: TestClient is ready
        - Act: Call GET /activities
        - Assert: Verify participants contain valid email-like strings
        """
        # Arrange
        # (client fixture already set up)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation

    def test_get_activities_participant_count_valid(self, client):
        """
        Test that participant count doesn't exceed max_participants.
        
        AAA Pattern:
        - Arrange: TestClient is ready
        - Act: Call GET /activities
        - Assert: Verify participant count <= max_participants
        """
        # Arrange
        # (client fixture already set up)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            participant_count = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            assert participant_count <= max_participants, \
                f"{activity_name} has more participants than allowed"
