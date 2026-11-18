"""
Pytest configuration and shared fixtures for FastAPI tests.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """
    Provide a TestClient for making HTTP requests to the FastAPI app.
    
    This fixture creates a fresh app instance for each test to ensure
    test isolation and prevent state leakage between tests.
    """
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Provide a sample email for testing."""
    return "test_student@mergington.edu"


@pytest.fixture
def sample_activity():
    """Provide a sample activity name for testing."""
    return "Chess Club"
