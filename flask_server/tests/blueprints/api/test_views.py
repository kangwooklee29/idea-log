"""
flask_server/tests/blueprints/api/test_views.py
"""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

import pytest
from ....models import Category
from ....app import create_app
from ....dao import category_dao

app = create_app(True)
with app.app_context():
    category_dao.create_categories_for_user("test_user")


@pytest.fixture
def test_client():
    """Provide a test client for the Flask app.

    Returns:
        Flask test client instance.
    """
    with app.test_client() as client:
        yield client


def test_not_authenticated(test_client):
    """Ensure unauthenticated requests are rejected with a 401 status.

    Args:
        test_client (Flask test client): A test client instance for the Flask app.

    Returns:
        None: This function only asserts expected outcomes.
    """
    response = test_client.get('/api/profile')
    assert response.status_code == 401
    assert response.get_json() == {"error": "Not authenticated"}


def test_invalid_property_request(test_client):
    """Ensure requests with invalid properties return a 400 status.

    Args:
        test_client (Flask test client): A test client instance for the Flask app.

    Returns:
        None: This function only asserts expected outcomes.
    """
    with test_client.session_transaction() as sess:
        sess['profile'] = {'name': 'guest'}
    response = test_client.get('/api/profile',
                               query_string={'property': 'invalid_property'})
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "'invalid_property' is not a valid property."
    }


def test_valid_property_request(test_client):
    """Test a valid property request.

    This test simulates a session where a 'profile' exists and checks for the expected value
    of the 'name' property in the response.

    Args:
        test_client (Flask test client): A test client instance for the Flask app.

    Returns:
        None: This function only asserts expected outcomes.
    """
    with test_client.session_transaction() as sess:
        sess['profile'] = {'name': 'guest'}
    response = test_client.get('/api/profile',
                               query_string={'property': 'name'})
    assert response.get_json() == {"value": "guest"}


@pytest.fixture
def mock_fetch_by_user_id():
    """
    Mock the fetch_by_user_id method to return a predefined list of categories.
    """
    with app.app_context():
        category_dao.fetch_by_user_id("test_user")


def test_fetch_categories(test_client, mock_fetch_by_user_id):
    """
    Test fetching categories for a user.

    Args:
        test_client (FlaskClient): Flask test client instance.
        mock_fetch_by_user_id (MagicMock): Mocked method returning predefined categories.

    Returns:
        None
    """
    with test_client.session_transaction() as sess:
        sess['profile'] = {'id': 'test_user'}

    response = test_client.get('/api/fetch_categories')
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 3
    assert data[0]['id'] == 1
    assert data[0]['name'] == "All"
    assert data[0]['user_id'] == "test_user"
    assert data[1]['id'] == 2
    assert data[1]['name'] == "None"
    assert data[1]['user_id'] == "test_user"
    assert data[2]['id'] == 3
    assert data[2]['name'] == "Deleted"
    assert data[2]['user_id'] == "test_user"


def test_update_category(test_client):
    """Test updating an existing category.
    
    Given:
        A category ID, name, and user ID.
    When:
        The '/api/update_category' endpoint is hit.
    Then:
        The category's name should be updated correctly.
    """
    with test_client.session_transaction() as sess:
        sess['profile'] = {'id': 'test_user'}

    response = test_client.get(
        '/api/update_category?name=UpdatedCategory&id=1')
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['success'] is True

    category = Category.query.get(1)
    assert category.name == 'UpdatedCategory'


def test_create_new_category(test_client):
    """Test creating a new category.
    
    Given:
        A name and user ID but no category ID.
    When:
        The '/api/update_category' endpoint is hit.
    Then:
        A new category should be created.
    """
    with test_client.session_transaction() as sess:
        sess['profile'] = {'id': 'test_user'}

    response = test_client.get('/api/update_category?name=NewCategory')
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['success'] is True

    category = Category.query.filter_by(name='NewCategory').first()
    assert category is not None


def test_update_invalid_category(test_client):
    """Test updating a category with an invalid ID.
    
    Given:
        An invalid category ID.
    When:
        The '/api/update_category' endpoint is hit.
    Then:
        The update should fail and return success as False.
    """
    with test_client.session_transaction() as sess:
        sess['profile'] = {'id': 'test_user'}

    response = test_client.get('/api/update_category?name=NewCategory&id=9999')
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['success'] is False
