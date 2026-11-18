"""
Tests for DELETE /unregister endpoint using AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestUnregisterEndpoint:
    """Test suite for the DELETE /unregister endpoint."""

    def test_unregister_successful(self, client, sample_activity):
        """
        Test successful unregistration from an activity.
        
        AAA Pattern:
        - Arrange: Sign up a student first
        - Act: Call DELETE /unregister endpoint
        - Assert: Verify success response and participant removed
        """
        # Arrange
        email = "unregister_test@mergington.edu"
        activity_name = sample_activity
        
        # First sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "Unregistered" in result["message"]
        assert email in result["message"]

    def test_unregister_participant_removed_from_list(self, client, sample_activity):
        """
        Test that participant is actually removed from activity's list.
        
        AAA Pattern:
        - Arrange: Sign up a student
        - Act: Unregister and fetch activities
        - Assert: Verify participant no longer in list
        """
        # Arrange
        email = "remove_me@mergington.edu"
        activity_name = sample_activity
        
        # Sign up first
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()
        
        # Assert
        assert response.status_code == 200
        participants = activities[activity_name]["participants"]
        assert email not in participants

    def test_unregister_nonexistent_activity(self, client):
        """
        Test unregister for non-existent activity returns 404.
        
        AAA Pattern:
        - Arrange: Set up invalid activity name
        - Act: Try to unregister from non-existent activity
        - Assert: Verify 404 error
        """
        # Arrange
        fake_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{fake_activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_unregister_student_not_signed_up(self, client, sample_activity):
        """
        Test unregister for student not signed up returns 400.
        
        AAA Pattern:
        - Arrange: Set up data (student not signed up)
        - Act: Try to unregister student who isn't signed up
        - Assert: Verify 400 error
        """
        # Arrange
        email = "not_signed_up@mergington.edu"
        activity_name = sample_activity
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "not signed up" in result["detail"].lower()

    def test_unregister_then_signup_again(self, client, sample_activity):
        """
        Test that a student can unregister and then sign up again.
        
        AAA Pattern:
        - Arrange: Sign up a student
        - Act: Unregister, then sign up again
        - Assert: Verify student is in list after re-signup
        """
        # Arrange
        email = "reregister@mergington.edu"
        activity_name = sample_activity
        
        # First signup
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Sign up again
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert unregister_response.status_code == 200
        assert signup_response.status_code == 200
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_unregister_multiple_students_independent(self, client, sample_activity):
        """
        Test that unregistering one student doesn't affect others.
        
        AAA Pattern:
        - Arrange: Sign up multiple students
        - Act: Unregister one student
        - Assert: Verify only one is removed, others remain
        """
        # Arrange
        activity_name = sample_activity
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        email3 = "student3@mergington.edu"
        
        # Sign up all three
        for email in [email1, email2, email3]:
            client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email2}"
        )
        
        # Assert
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]
        
        assert email1 in participants
        assert email2 not in participants
        assert email3 in participants

    def test_unregister_increases_availability(self, client, sample_activity):
        """
        Test that unregistering opens up a spot for new signups.
        
        AAA Pattern:
        - Arrange: Fill activity to capacity with one student reserved
        - Act: Unregister one student
        - Assert: Verify new student can sign up (capacity available)
        """
        # Arrange
        activity_name = "Basketball Team"  # max_participants: 15
        # Sign up 15 students
        emails = [f"player{i}@mergington.edu" for i in range(15)]
        
        for email in emails:
            client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # At this point, should be at capacity
        response_full = client.post(
            f"/activities/{activity_name}/signup?email=extra@mergington.edu"
        )
        assert response_full.status_code == 400  # Should fail - at capacity
        
        # Act
        # Unregister one student
        client.delete(
            f"/activities/{activity_name}/unregister?email={emails[0]}"
        )
        
        # Try to sign up with the extra student
        response_after_unregister = client.post(
            f"/activities/{activity_name}/signup?email=extra@mergington.edu"
        )
        
        # Assert
        assert response_after_unregister.status_code == 200  # Should succeed now
