"""
flask_server/tests/blueprints/api/test_views.py
"""

import pytest
from ....app import create_app


@pytest.fixture
def test_client():
    """Provide a test client for the Flask app.

    Returns:
        Flask test client instance.
    """
    app = create_app()
    with app.test_client() as client:
        yield client


def test_not_authenticated(client):
    """Ensure unauthenticated requests are rejected with a 401 status.

    Args:
        client (Flask test client): A test client instance for the Flask app.

    Returns:
        None: This function only asserts expected outcomes.
    """
    response = client.get('/api/profile')
    assert response.status_code == 401
    assert response.get_json() == {"error": "Not authenticated"}


def test_invalid_property_request(client):
    """Ensure requests with invalid properties return a 400 status.

    Args:
        client (Flask test client): A test client instance for the Flask app.

    Returns:
        None: This function only asserts expected outcomes.
    """
    with client.session_transaction() as sess:
        sess['profile'] = {'name': 'guest'}
    response = client.get('/api/profile',
                          query_string={'property': 'invalid_property'})
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "'invalid_property' is not a valid property."
    }


def test_valid_property_request(client):
    """Test a valid property request.

    This test simulates a session where a 'profile' exists and checks for the expected value
    of the 'name' property in the response.

    Args:
        client (Flask test client): A test client instance for the Flask app.

    Returns:
        None: This function only asserts expected outcomes.
    """
    with client.session_transaction() as sess:
        sess['profile'] = {'name': 'guest'}
    response = client.get('/api/profile', query_string={'property': 'name'})
    assert response.get_json() == {"value": "guest"}
