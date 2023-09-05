"""
flask_server/blueprints/main/views.py
"""

from flask import Blueprint, current_app, send_from_directory, session

blueprint = Blueprint('main', __name__)


@blueprint.route('/')
def index():
    """
    Serve a index page file.

    Returns:
    - Response: The static file as a Flask response object.
    """
    if 'profile' in session:
        return send_from_directory(current_app.static_folder,
                                   'index-authenticated.html')
    return send_from_directory(current_app.static_folder, 'index-guest.html')


@blueprint.route('/<path:filename>')
def serve_static(filename):
    """
    Serve a static file.

    Args:
    - filename (str): The path to the file within the static directory.

    Returns:
    - Response: The static file as a Flask response object.
    """
    return send_from_directory(current_app.static_folder, filename)
