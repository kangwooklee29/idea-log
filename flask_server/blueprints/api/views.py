from flask import Blueprint, jsonify, request, session
from flask_server import models
from urllib.parse import unquote

blueprint_api = Blueprint('api', __name__)

ALLOWED_PROPERTIES_API_PROFILE = {'name'}

@blueprint_api.route('/profile')
def handle_api_profile():
    prop = request.args.get('property', default='')

    if not prop in ALLOWED_PROPERTIES_API_PROFILE:
        return jsonify(error=f"'{prop}' is not a valid property."), 400

    value = ''
    if 'profile' in session:
        value = session.get('profile').get(prop, '')

    return jsonify(value=value)

@blueprint_api.route('/fetch_categories')
def fetch_categories():
    return jsonify([cat.to_dict() for cat in models.fetch_categories(session.get('profile')['id'])])    

@blueprint_api.route('/write_message')
def write_message():
    message = unquote(request.args.get('message', default=''))
    written_date = request.args.get('written_date', default='')
    category_id = request.args.get('category_id', default='')
    msg_id = request.args.get('msg_id', default='')

    if models.write_message(message, written_date, category_id, msg_id, session.get('profile')['id']):
        return jsonify(success=True)
    return jsonify(success=False)

@blueprint_api.route('/update_category')
def update_category():
    name = unquote(request.args.get('name', default=''))
    category_id = request.args.get('id', default='')

    if models.update_category(name, category_id, session.get('profile')['id']):
        return jsonify(success=True)
    return jsonify(success=False)

@blueprint_api.route('/fetch_messages')
def fetch_messages():
    target = request.args.get('target')
    limit = request.args.get('limit')
    parent_msg_id = request.args.get('parent_msg_id')
    target_date = request.args.get('target_date')
    category_id = request.args.get('category_id')

    return models.fetch_messages(target, limit, parent_msg_id, target_date, category_id,  session.get('profile')['id'])
