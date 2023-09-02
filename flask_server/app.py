from authlib.integrations.flask_client import OAuth
from decouple import config
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from .routes import blueprint

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

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
