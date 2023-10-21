"""
flask_server/app.py
"""

from authlib.integrations.flask_client import OAuth

# pylint: disable=no-name-in-module
from decouple import config

from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_server import models
from .blueprints import blueprint, blueprint_auth, blueprint_api

STATIC_FOLDER = "../web_client"


def create_app(is_test: bool = False):
    """
    Create a Flask app

    Returns:
    - Response: A Flask object
    """
    flask_app = Flask(__name__,
                      static_url_path='',
                      static_folder=STATIC_FOLDER)
    flask_app.config[
        'SESSION_COOKIE_SECURE'] = True  # allow HTTPS only for session cookie
    if is_test is False:
        CORS(flask_app,
             origins=[config('DOMAIN_NAME')
                      ])  # allow requests only from the configured domain name
        flask_app.wsgi_app = ProxyFix(  # type: ignore
            flask_app.wsgi_app, x_proto=1)
        flask_app.google_oauth = OAuth(flask_app).register(  # type: ignore
            name='google',
            client_id=config('GOOGLE_OAUTH_CLIENT_ID'),
            client_secret=config('GOOGLE_OAUTH_CLIENT_SECRET'),
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            authorize_params=None,
            access_token_url='https://accounts.google.com/o/oauth2/token',
            access_token_method='POST',
            refresh_token_url=None,
            redirect_to='authorized',
            client_kwargs={'scope': 'profile email'},
        )
    flask_app.secret_key = config('FLASK_SECRET_KEY')
    flask_app.register_blueprint(blueprint, url_prefix='')
    flask_app.register_blueprint(blueprint_auth, url_prefix='/auth')
    flask_app.register_blueprint(blueprint_api, url_prefix='/api')

    # Initialize db
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + config(
        'SQLALCHEMY_DATABASE_URI')
    flask_app.db = models.db  # type: ignore
    flask_app.db.init_app(flask_app)  # type: ignore

    # Create tables if they do not exist already
    with flask_app.app_context():
        flask_app.db.create_all()  # type: ignore

    return flask_app
