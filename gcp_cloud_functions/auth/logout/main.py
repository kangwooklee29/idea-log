"""
gcp_cloud_functions/auth/logout/main.py
"""

import firebase_admin  # pylint: disable=import-error
import requests
from flask import redirect, make_response
from firebase_admin import firestore  # pylint: disable=import-error


def logout(request):
    """
    Handle Logout Action
    """
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    db = firestore.client()

    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect('/')

    doc_ref = db.collection('sessions').document(session_id)
    doc = doc_ref.get()
    if not doc.exists:
        return redirect('/')

    try:
        access_token = doc_ref.get().to_dict().get('access_token')
        response = requests.post('https://oauth2.googleapis.com/revoke',
                                 data={'token': access_token},
                                 timeout=10)
        if response.status_code != 200:
            print("Token revocation failed. Error:", response.text)

        doc_ref.delete()
        response = make_response(redirect('/'))
        response.headers[
            'Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    except Exception as e:
        return str(e), 500

    return response
