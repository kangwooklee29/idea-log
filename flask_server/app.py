import requests
from flask import Flask, redirect, send_from_directory, session, url_for
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix

STATIC_FOLDER = "../web_client"

app = Flask(__name__, static_url_path='', static_folder=STATIC_FOLDER)
app.secret_key = 'your_very_secret_key_here'
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='',
    client_secret='',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_method='POST',
    refresh_token_url=None,
    redirect_to='authorized',
    client_kwargs={'scope': 'profile email'},
)

@app.route('/')
def index():
    if 'profile' in session:
        return send_from_directory(app.static_folder, 'index-authenticated.html')
    return send_from_directory(app.static_folder, 'index-guest.html')

@app.route('/login')
def login():
    if 'profile' in session:
        return redirect(url_for('index'))
    return google.authorize_redirect(url_for('authorized', _external=True), prompt='consent')

@app.route('/login/callback')
def authorized():
    token = google.authorize_access_token()
    resp = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
    session['profile'] = resp.json()
    session['access_token'] = token['access_token']
    google_profile = session.get('profile')
    print(google_profile['id'])
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    access_token = session.get('access_token')
    if access_token:
        response = requests.post('https://oauth2.googleapis.com/revoke', data={'token': access_token})
        if response.status_code != 200:
            print("Token revocation failed. Error:", response.text)

    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
