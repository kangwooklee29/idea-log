from flask import Blueprint, current_app, send_from_directory, session

blueprint = Blueprint('main', __name__)

@blueprint.route('/')
def index():
    if 'profile' in session:
        return send_from_directory(current_app.static_folder, 'index-authenticated.html')
    return send_from_directory(current_app.static_folder, 'index-guest.html')

@blueprint.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)
