"""
gcp_app_engine/blueprints/auth/views.py
"""

from flask import Blueprint, current_app, jsonify, redirect, request, send_from_directory
from flask import session, url_for
import requests

from dao import category_dao

blueprint_auth = Blueprint('auth', __name__)


@blueprint_auth.route('/login')
def login():
    """
    Handle Google Login request.

    Returns:
    - Response: Google OAuth Authorize Redirect
    """
    if 'profile' in session:
        return redirect(url_for('main.index'))
    return current_app.google_oauth.authorize_redirect(url_for(
        'auth.authorized', _external=True),
                                                       prompt='consent')


@blueprint_auth.route('/login/callback', methods=['GET', 'POST'])
def authorized():
    """
    Process the login request and redirect to the index page or join page.

    Returns:
    - Response: The redirect object
    """

    is_guest = request.args.get('guest', default=False, type=bool)
    if is_guest:
        session['profile'] = {'id': 'guest', 'name': 'guest'}
    elif 'state' not in request.args:
        # Invalid state, possibly due to CSRF
        return "Invalid state parameter", 400
    else:
        token = current_app.google_oauth.authorize_access_token()
        session['profile'] = current_app.google_oauth.get(
            'https://www.googleapis.com/oauth2/v1/userinfo').json()
        session['access_token'] = token['access_token']

    if category_dao.check_if_joined(session.get('profile')['id']):
        return redirect(url_for('main.index'))
    return redirect(url_for('auth.user_join'))


@blueprint_auth.route('/join')
def user_join():
    """
    Process the join request

    Returns:
    - Response: The static file as a Flask response object.
    """
    action = request.args.get('action')
    if action:
        return handle_join_action(action)

    return send_from_directory(current_app.static_folder,
                               'src/pages/join.html')


def handle_join_action(action=None):
    """
    1. 가입에 동의: 가입을 시도하고, 성공 시 성공 메시지 띄우고 index로. 실패 시 재가입 시도하라고 메시지 띄우고 로그아웃.
    2. 가입에 미동의: 경고 메시지 띄우고 로그아웃.
    3. 알 수 없는 action: join으로 redirect
    """

    if action == 'agree':
        if category_dao.create_categories_for_user(
                session.get('profile')['id']):
            return jsonify({
                'message': 'Successfully joined!',
                'redirect_url': url_for('main.index')
            })
        return jsonify({
            'message': 'Failed to join.',
            'redirect_url': url_for('auth.logout')
        })
    if action == 'disagree':
        return jsonify({
            'message': 'You must join to use the service.',
            'redirect_url': url_for('auth.logout')
        })

    return jsonify({'message': '', 'redirect_url': url_for('auth.user_join')})


@blueprint_auth.route('/logout')
def logout():
    """
    Process the logout request

    Returns:
    - Response: The redirect object
    """
    access_token = session.get('access_token')
    if access_token:
        response = requests.post('https://oauth2.googleapis.com/revoke',
                                 data={'token': access_token},
                                 timeout=10)
        if response.status_code != 200:
            print("Token revocation failed. Error:", response.text)

    session.clear()
    return redirect(url_for('main.index'))
