from authlib.integrations.flask_client import OAuth
from decouple import config
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_server import models
from .blueprints import blueprint, blueprint_auth, blueprint_api

STATIC_FOLDER = "../web_client"

def create_app():
    app = Flask(__name__, static_url_path='', static_folder=STATIC_FOLDER)
    app.secret_key = config('FLASK_SECRET_KEY')
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)
    app.google_oauth = OAuth(app).register(
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
    app.register_blueprint(blueprint, url_prefix='')
    app.register_blueprint(blueprint_auth, url_prefix='/auth')
    app.register_blueprint(blueprint_api, url_prefix='/api')

    # Initialize db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + config('SQLALCHEMY_DATABASE_URI')
    app.db = models.db
    app.db.init_app(app)

    # Create tables if they do not exist already
    with app.app_context():
        app.db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
