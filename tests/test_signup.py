"""
Tests for POST /signup endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestSignupEndpoint:
    """Test suite for the POST /signup endpoint."""

    def test_signup_successful(self, client, sample_activity, sample_email):
        """
        Test successful signup for an activity.
        
        AAA Pattern:
        - Arrange: Set up test data (new email, existing activity)
        - Act: Call POST /signup endpoint
        - Assert: Verify success response and participant added
        """
        # Arrange
        new_email = "new_student@mergington.edu"
        activity_name = sample_activity
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "Signed up" in result["message"]
        assert new_email in result["message"]
        assert activity_name in result["message"]

    def test_signup_participant_added_to_list(self, client, sample_activity):
        """
        Test that participant is actually added to activity's participant list.
        
        AAA Pattern:
        - Arrange: Set up test data
        - Act: Sign up and then fetch activities
        - Assert: Verify participant appears in the list
        """
        # Arrange
        new_email = "verify_signup@mergington.edu"
        activity_name = sample_activity
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert response.status_code == 200
        participants = activities[activity_name]["participants"]
        assert new_email in participants

    def test_signup_nonexistent_activity(self, client):
        """
        Test signup for a non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: Set up invalid activity name
        - Act: Try to sign up for non-existent activity
        - Assert: Verify 404 error
        """
        # Arrange
        fake_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_signup_duplicate_registration(self, client, sample_activity):
        """
        Test that duplicate signup is rejected with 400.
        
        AAA Pattern:
        - Arrange: Set up data and register once
        - Act: Try to register the same email again
        - Assert: Verify 400 error for duplicate
        """
        # Arrange
        email = "duplicate_test@mergington.edu"
        activity_name = sample_activity
        
        # First signup
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act
        # Try to sign up again
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"].lower()

    def test_signup_at_capacity(self, client):
        """
        Test that signup is rejected when activity is at capacity.
        
        AAA Pattern:
        - Arrange: Create a small activity and fill it to capacity
        - Act: Try to sign up when at capacity
        - Assert: Verify 400 error for full activity
        """
        # Arrange
        activity_name = "Basketball Team"  # Has max_participants: 15
        # We'll sign up enough people to fill most of it
        emails_to_signup = [
            f"player{i}@mergington.edu" for i in range(15)
        ]
        
        # Sign up students until capacity
        for email in emails_to_signup:
            client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act
        # Try to sign up one more (should exceed capacity)
        over_capacity_email = "extra_player@mergington.edu"
        response = client.post(
            f"/activities/{activity_name}/signup?email={over_capacity_email}"
        )
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "full" in result["detail"].lower() or "capacity" in result["detail"].lower()

    def test_signup_multiple_different_activities(self, client):
        """
        Test that a student can sign up for multiple different activities.
        
        AAA Pattern:
        - Arrange: Set up test data with multiple activities
        - Act: Sign up same student for different activities
        - Assert: Verify success for each signup
        """
        # Arrange
        email = "multi_activity@mergington.edu"
        activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act & Assert for each activity
        for activity in activities:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
            
        # Verify student is in all activities
        activities_response = client.get("/activities")
        all_activities = activities_response.json()
        for activity in activities:
            assert email in all_activities[activity]["participants"]
