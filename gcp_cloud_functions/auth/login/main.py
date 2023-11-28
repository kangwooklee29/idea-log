"""
gcp_cloud_functions/auth/login/main.py
"""

import firebase_admin  # pylint: disable=import-error
import google_auth_oauthlib.flow  # pylint: disable=import-error
import json
from flask import redirect, make_response
from firebase_admin import firestore  # pylint: disable=import-error

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'openid']


def login(request):
    with open(CLIENT_SECRETS_FILE, 'r') as file:
        data = json.load(file)

    try:
        session_id = request.cookies.get('session_id')
        if not session_id:
            return redirect('/')

        if not firebase_admin._apps:
            firebase_admin.initialize_app()
        db = firestore.client()

        # 로그인하지 않은 상태라면 session_id가 임의의 값이라 db에 존재하지 않고,
        # 로그인한 상태라면 session_id가 db에 존재하는 값으로 대치돼서 클라이언트가 보관하고 있는 상태.
        # 즉 session_id가 db에 존재한다면 이미 로그인한 상태라 로그인이 불필요.
        if db.collection('sessions').document(session_id).get().exists:
            return redirect('/')

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES)
        flow.redirect_uri = data['web']['redirect_uris'][0]

        authorization_url, state = flow.authorization_url(
            access_type='offline', include_granted_scopes='true')

        _, doc_ref = db.collection('sessions').add({'state': state})
        response = make_response(redirect(authorization_url))
        response.set_cookie('session_id', doc_ref.id)

        return response
    except Exception as e:
        return str(e), 500
