"""
gcp_cloud_functions/auth/login_callback/main.py
"""

import json
import re
import firebase_admin  # pylint: disable=import-error
import google_auth_oauthlib.flow  # pylint: disable=import-error
import requests
from datetime import datetime, timedelta
from flask import redirect, make_response
from firebase_admin import firestore  # pylint: disable=import-error

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email', 'openid',
    'https://www.googleapis.com/auth/userinfo.profile'
]
DNS_PATTERN = r'https?://[^/]+/'

if not firebase_admin._apps:
    firebase_admin.initialize_app()
db = firestore.client()


def check_if_joined(user_id):
    """Checks if the user is joined"""
    result = db.collection('category').where('user_id', '==',
                                             user_id).limit(1).stream()
    return next(result, None) is not None


def login_callback(request):
    """Handles login callback request"""
    with open(CLIENT_SECRETS_FILE, 'r') as file:
        data = json.load(file)

    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect('/')

    response = make_response(redirect('/'))
    response.headers[
        'Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'

    is_guest = request.args.get('guest', default=False, type=bool)
    if is_guest:
        profile = {'id': 'guest', 'name': 'guest'}
        _, doc_ref = db.collection('sessions').add({'profile': profile})
        session_id = doc_ref.id
    else:
        doc_ref = db.collection('sessions').document(session_id)
        doc = doc_ref.get()
        if not doc.exists:
            return redirect('/')

        state = doc.to_dict().get('state')
        if not state or 'state' not in request.args or state != request.args[
                'state']:
            # Invalid state, possibly due to CSRF
            return "Invalid state parameter", 400

        try:
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
            flow.redirect_uri = data['web']['redirect_uris'][0]
            replaced_url = re.sub(DNS_PATTERN, flow.redirect_uri, request.url)
            flow.fetch_token(authorization_response=replaced_url)
            access_token = flow.credentials.token
            profile = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={
                    'Authorization': f'Bearer {access_token}'
                }).json()
            query = db.collection('sessions').where('profile.id', '==',
                                                    profile['id']).stream()
            for doc in query:
                doc.reference.delete()

            doc_ref.update({'access_token': access_token, 'profile': profile})
        except Exception as e:
            return str(e), 500

    response.set_cookie('session_id',
                        session_id,
                        expires=datetime.now() + timedelta(days=90))

    if check_if_joined(profile['id']):
        return response

    response.headers['Location'] = '/auth/join'
    return response
