"""
gcp_app_engine/blueprints/api/views.py
"""

from urllib.parse import unquote
from flask import Blueprint, jsonify, request, session
from dao import category_dao, message_dao, user_dao

blueprint_api = Blueprint('api', __name__)

ALLOWED_PROPERTIES_API_PROFILE = {'name'}


@blueprint_api.before_request
def verify_authentication():
    """
    Verify if the user is authenticated before processing the request.

    Returns:
    - Response: JSON message
    """
    if 'profile' not in session:
        return jsonify({"error": "Not authenticated, You need to log in."}), 401
    return None


@blueprint_api.route('/profile')
def handle_api_profile():
    """
    Fetch the Google user profile

    Returns:
    - Response: JSON message
    """
    prop = request.args.get('property', default='')

    if not prop in ALLOWED_PROPERTIES_API_PROFILE:
        return jsonify(error=f"'{prop}' is not a valid property."), 400

    value = ''
    if 'profile' in session:
        value = session.get('profile').get(prop, '')

    return jsonify(value=value)


@blueprint_api.route('/fetch_categories')
def fetch_categories():
    """
    Fetch all the categories using category_dao.fetch_by_user_id

    Returns:
    - Response: JSON message
    """
    return jsonify(category_dao.fetch_by_user_id(session.get('profile')['id']))


@blueprint_api.route('/write_message', methods=['POST'])
def write_message():
    """
    Write a message using message_dao.write_message

    Returns:
    - Response: JSON message
    """
    if message_dao.write_message({
            'user_id': session.get('profile')['id'],
            **request.json
    }):
        return jsonify(success=True)
    return jsonify(success=False)


@blueprint_api.route('/update_category')
def update_category():
    """
    Update the category name using category_dao.update_category

    Returns:
    - Response: JSON message
    """
    name = unquote(request.args.get('name', default=''))
    category_id = request.args.get('id', default='')

    updated_category_id = category_dao.update_category(
        name, category_id,
        session.get('profile')['id'])
    if updated_category_id:
        return jsonify(updated_category_id)
    return jsonify(success=False)


@blueprint_api.route('/fetch_messages')
def fetch_messages():
    """
    Fetch the message using message_dao.fetch_messages

    Returns:
    - Response: JSON message
    """
    target = request.args.get('target')
    limit = request.args.get('limit')
    parent_msg_id = request.args.get('parent_msg_id')
    target_date = request.args.get('target_date')
    category_id = request.args.get('category_id')

    return message_dao.fetch_messages(target=target,
                                      limit=limit,
                                      parent_msg_id=parent_msg_id,
                                      target_date=target_date,
                                      category_id=category_id,
                                      user_id=session.get('profile')['id'])


@blueprint_api.route('/fetch_options')
def fetch_options():
    """
    Fetch all the options for the given user id

    Returns:
    - Response: JSON message
    """
    return jsonify(user_dao.fetch_by_user_id(session.get('profile')['id']))


@blueprint_api.route('/update_options', methods=['POST'])
def update_options():
    """
    Update all the options for the given user id

    Returns:
    - Response: JSON message
    """
    api_key = request.json['api_key']
    username = request.json['username']
    return jsonify(user_dao.update_by_user_id(api_key=api_key,
                                              username=username,
                                              user_id=session.get('profile')['id']))
