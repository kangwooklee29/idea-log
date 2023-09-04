from flask import Blueprint, current_app, jsonify, redirect, request, send_from_directory, session, url_for
from flask_server import models
import requests

blueprint = Blueprint('main', __name__)

@blueprint.route('/')
def index():
    if 'profile' in session:
        return send_from_directory(current_app.static_folder, 'index-authenticated.html')
    return send_from_directory(current_app.static_folder, 'index-guest.html')

@blueprint.route('/get_username')
def get_username():
    if 'profile' in session:
        return jsonify({"name": session.get('profile')['name']})
    return jsonify({"name": None})

@blueprint.route('/login')
def login():
    if 'profile' in session:
        return redirect(url_for('main.index'))
    return current_app.google_oauth.authorize_redirect(url_for('main.authorized', _external=True), prompt='consent')

@blueprint.route('/login/callback', methods=['GET', 'POST'])
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
    return redirect(url_for('main.user_join'))

@blueprint.route('/join')
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
            return jsonify({'message': 'Failed to join.', 'redirect_url': url_for('main.logout')})
    elif action == 'disagree':
        return jsonify({'message': 'You must join to use the service.', 'redirect_url': url_for('main.logout')})

    return jsonify({'message': '', 'redirect_url': url_for('main.user_join')})

@blueprint.route('/logout')
def logout():
    access_token = session.get('access_token')
    if access_token:
        response = requests.post('https://oauth2.googleapis.com/revoke', data={'token': access_token})
        if response.status_code != 200:
            print("Token revocation failed. Error:", response.text)

    session.clear()
    return redirect(url_for('main.index'))
