"""
gcp_cloud_functions/auth/login_callback/main.py
"""

import firebase_admin  # pylint: disable=import-error
import google_auth_oauthlib.flow  # pylint: disable=import-error
import json
import re
import requests
from flask import redirect
from firebase_admin import firestore  # pylint: disable=import-error

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'openid']
DNS_PATTERN = r'https?://[^/]+/'

if not firebase_admin._apps:
    firebase_admin.initialize_app()
db = firestore.client()


def check_if_joined(user_id):
    result = db.collection('category').where('user_id', '==',
                                             user_id).limit(1).stream()
    return next(result, None) is not None


def login_callback(request):
    with open(CLIENT_SECRETS_FILE, 'r') as file:
        data = json.load(file)

    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect('/')

    doc_ref = db.collection('sessions').document(session_id)
    doc = doc_ref.get()
    if not doc.exists:
        return redirect('/')

    state = doc.to_dict().get('state')
    if not state or 'state' not in request.args or state != request.args[
            'state']:
        # Invalid state, possibly due to CSRF
        return "Invalid state parameter", 400

    is_guest = request.args.get('guest', default=False, type=bool)
    if is_guest:
        doc_ref.update({'profile': {'id': 'guest', 'name': 'guest'}})
    else:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
        flow.redirect_uri = data['web']['redirect_uris'][0]
        replaced_url = re.sub(DNS_PATTERN, flow.redirect_uri, request.url)
        flow.fetch_token(authorization_response=replaced_url)
        access_token = flow.credentials.token
        profile = requests.get('https://www.googleapis.com/oauth2/v2/userinfo',
                               headers={
                                   'Authorization': f'Bearer {access_token}'
                               }).json()
        doc_ref.update({'access_token': access_token, 'profile': profile})

    if check_if_joined(profile['id']):
        return redirect('/')
    return redirect('/auth/join')
