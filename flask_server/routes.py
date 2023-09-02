from flask import Blueprint, current_app, redirect, send_from_directory, session, url_for
import requests

blueprint = Blueprint('main', __name__)

@blueprint.route('/')
def index():
    if 'profile' in session:
        return send_from_directory(current_app.static_folder, 'index-authenticated.html')
    return send_from_directory(current_app.static_folder, 'index-guest.html')

@blueprint.route('/login')
def login():
    if 'profile' in session:
        return redirect(url_for('main.index'))
    return current_app.google_oauth.authorize_redirect(url_for('main.authorized', _external=True), prompt='consent')

@blueprint.route('/login/callback')
def authorized():
    token = current_app.google_oauth.authorize_access_token()
    session['profile'] = current_app.google_oauth.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
    session['access_token'] = token['access_token']
    print(session.get('profile')['id'])
    return redirect(url_for('main.index'))

@blueprint.route('/logout')
def logout():
    access_token = session.get('access_token')
    if access_token:
        response = requests.post('https://oauth2.googleapis.com/revoke', data={'token': access_token})
        if response.status_code != 200:
            print("Token revocation failed. Error:", response.text)

    session.clear()
    return redirect(url_for('main.index'))
