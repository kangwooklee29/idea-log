"""
gcp_cloud_functions/get_static_file/main.py
"""

import gzip
import logging
import uuid
import firebase_admin  # pylint: disable=import-error
import requests
from flask import make_response
from firebase_admin import firestore  # pylint: disable=import-error


def get_static_file(request):
    """HTTP Cloud Function."""

    logging.basicConfig(level=logging.INFO)

    path = request.path
    base_url = 'https://kangwooklee29.github.io/idea-log/web_client'

    session_id = request.cookies.get('session_id')
    if path in ('', '/'):
        try:
            if not firebase_admin._apps:
                firebase_admin.initialize_app()
            db = firestore.client()
            if session_id and db.collection('sessions').document(
                    session_id).get().exists:
                path = '/src/pages/index-authenticated.html'
            else:
                path = '/src/pages/index-guest.html'
        except Exception as e:
            return str(e), 500

    file_url = f'{base_url}{path}'

    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        if 'gzip' in response.headers.get('Content-Encoding', ''):
            content = gzip.decompress(response.raw.read())
        else:
            content = response.content

        headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() != 'content-encoding'
        }

        response = make_response((content, response.status_code, headers))

        if "index" in path:
            response.headers[
                'Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'

        if not session_id:
            response.set_cookie('session_id', str(uuid.uuid4()))

        return response
    except requests.exceptions.RequestException as e:
        logging.error('RequestException: %s', e)
        return ('File not found', 404, {'Content-Type': 'text/plain'})
    except Exception as e:
        logging.error('Unexpected error: %s', e)
        return ('Internal Server Error', 500, {'Content-Type': 'text/plain'})
