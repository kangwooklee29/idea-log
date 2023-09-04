from flask import Blueprint, current_app, jsonify, redirect, request, send_from_directory, session, url_for
from flask_server import models
from urllib.parse import unquote
import requests

blueprint = Blueprint('main', __name__)
blueprint_auth = Blueprint('auth', __name__)
blueprint_api = Blueprint('api', __name__)

ALLOWED_PROPERTIES_API_PROFILE = {'name'}

@blueprint.route('/')
def index():
    if 'profile' in session:
        return send_from_directory(current_app.static_folder, 'index-authenticated.html')
    return send_from_directory(current_app.static_folder, 'index-guest.html')

@blueprint.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

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

@blueprint_auth.route('/login')
def login():
    if 'profile' in session:
        return redirect(url_for('main.index'))
    return current_app.google_oauth.authorize_redirect(url_for('auth.authorized', _external=True), prompt='consent')

@blueprint_auth.route('/login/callback', methods=['GET', 'POST'])
def authorized():
    is_guest = request.args.get('guest', default=False, type=bool)

    if is_guest:
        session['profile'] = {'id': 'guest', 'name': 'guest'}
    else:
        token = current_app.google_oauth.authorize_access_token()
        session['profile'] = current_app.google_oauth.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
        session['access_token'] = token['access_token']

    if models.check_if_joined(session.get('profile')['id']):
        return redirect(url_for('main.index'))
    return redirect(url_for('auth.user_join'))

@blueprint_auth.route('/join')
def user_join():
    action = request.args.get('action')
    if action:
        return handle_join_action(action)

    return send_from_directory(current_app.static_folder, 'join.html')

def handle_join_action(action=None):
    """
    1. 가입에 동의: 가입을 시도하고, 성공 시 성공 메시지 띄우고 index로. 실패 시 재가입 시도하라고 메시지 띄우고 로그아웃.
    2. 가입에 미동의: 경고 메시지 띄우고 로그아웃.
    3. 알 수 없는 action: join으로 redirect
    """

    if action == 'agree':
        if models.create_categories_for_user(session.get('profile')['id']):
            return jsonify({'message': 'Successfully joined!', 'redirect_url': url_for('main.index')})
        else:
            return jsonify({'message': 'Failed to join.', 'redirect_url': url_for('auth.logout')})
    elif action == 'disagree':
        return jsonify({'message': 'You must join to use the service.', 'redirect_url': url_for('auth.logout')})

    return jsonify({'message': '', 'redirect_url': url_for('auth.user_join')})

@blueprint_auth.route('/logout')
def logout():
    access_token = session.get('access_token')
    if access_token:
        response = requests.post('https://oauth2.googleapis.com/revoke', data={'token': access_token})
        if response.status_code != 200:
            print("Token revocation failed. Error:", response.text)

    session.clear()
    return redirect(url_for('main.index'))
