"""
gcp_app_engine/main.py
"""

import json
from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_cors import CORS
from google.cloud import secretmanager
from urllib.parse import urlparse
from werkzeug.middleware.proxy_fix import ProxyFix
from blueprints import blueprint, blueprint_auth, blueprint_api

STATIC_FOLDER = "web_client"
CLIENT_SECRETS_FILE = "client_secret.json"


def create_app(is_test: bool = False):
    """
    Create a Flask app

    Returns:
    - Response: A Flask object
    """
    with open(CLIENT_SECRETS_FILE, 'r') as file:
        data = json.load(file)

    flask_app = Flask(__name__,
                      static_url_path='',
                      static_folder=STATIC_FOLDER)
    flask_app.config[
        'SESSION_COOKIE_SECURE'] = True  # allow HTTPS only for session cookie
    if is_test is False:
        CORS(flask_app,
             origins=[urlparse(data['web']['redirect_uris'][0]).netloc
                      ])  # allow requests only from the configured domain name
        flask_app.wsgi_app = ProxyFix(  # type: ignore
            flask_app.wsgi_app, x_proto=1)
        flask_app.google_oauth = OAuth(flask_app).register(  # type: ignore
            name='google',
            client_id=data['web']['client_id'],
            client_secret=data['web']['client_secret'],
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            authorize_params=None,
            access_token_url='https://accounts.google.com/o/oauth2/token',
            access_token_method='POST',
            refresh_token_url=None,
            redirect_to='authorized',
            client_kwargs={'scope': 'profile email'},
        )
    flask_app.secret_key = secretmanager.SecretManagerServiceClient() \
        .access_secret_version(name=f"projects/{data['web']['project_id']}/secrets/FLASK_SECRET_KEY/versions/latest") \
        .payload.data.decode('UTF-8')
    flask_app.register_blueprint(blueprint, url_prefix='')
    flask_app.register_blueprint(blueprint_auth, url_prefix='/auth')
    flask_app.register_blueprint(blueprint_api, url_prefix='/api')

    return flask_app


app = create_app()
