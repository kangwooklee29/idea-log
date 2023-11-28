"""
gcp_cloud_functions/auth/join/main.py
"""

import gzip
import firebase_admin  # pylint: disable=import-error
import requests
from flask import make_response, jsonify
from firebase_admin.exceptions import FirebaseError  # pylint: disable=import-error
from firebase_admin import firestore  # pylint: disable=import-error

DEFAULT_CATEGORIES = ['All', 'None', 'Deleted']
JOIN_FILE_URL = 'https://kangwooklee29.github.io/idea-log/web_client/src/pages/join.html'


def user_join(request):
    """HTTP Cloud Function."""

    action = request.args.get('action')
    if action:
        return handle_join_action(request.cookies.get('session_id'), action)

    try:
        response = requests.get(JOIN_FILE_URL, stream=True)
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

        return make_response((content, response.status_code, headers))
    except requests.exceptions.RequestException as e:
        return (f'File not found: {e}', 404, {'Content-Type': 'text/plain'})
    except Exception as e:
        print(f'Internal Server Error: {e}')
        return ('Internal Server Error', 500, {'Content-Type': 'text/plain'})


def create_categories_for_user(session_id):
    """
    A function that creates categories for the new user
    """

    if not session_id:
        return jsonify({
            'message': 'Session ID is missing',
            'redirect_url': '/'
        })

    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    db = firestore.client()

    try:
        doc = db.collection('sessions').document(session_id).get()
        if not doc.exists:
            return jsonify({
                'message': 'Session ID not found in Firestore',
                'redirect_url': '/'
            })

        user_id = doc.to_dict().get('profile')['id']
        for category_name in DEFAULT_CATEGORIES:
            db.collection('category').add({
                'name': category_name,
                'user_id': user_id
            })

        return jsonify({
            'message': 'Successfully joined!',
            'redirect_url': '/'
        })
    except FirebaseError as e:
        print(f"Error while adding new categories: {e}")
        return jsonify({
            'message': 'Failed to join',
            'redirect_url': '/auth/logout'
        })


def handle_join_action(session_id, action=None):
    """
    1. 가입에 동의: 가입을 시도하고, 성공 시 성공 메시지 띄우고 index로. 실패 시 재가입 시도하라고 메시지 띄우고 로그아웃.
    2. 가입에 미동의: 경고 메시지 띄우고 로그아웃.
    3. 알 수 없는 action: join으로 redirect
    """

    if action == 'agree':
        return create_categories_for_user(session_id)
    if action == 'disagree':
        return jsonify({
            'message': 'You must join to use the service.',
            'redirect_url': '/auth/logout'
        })

    return jsonify({'message': '', 'redirect_url': '/auth/join'})
