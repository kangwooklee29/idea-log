"""
gcp_cloud_functions/api/profile/main.py
"""

import firebase_admin  # pylint: disable=import-error
from firebase_admin import firestore  # pylint: disable=import-error
from flask import jsonify

if not firebase_admin._apps:
    firebase_admin.initialize_app()
db = firestore.client()

ALLOWED_PROPERTIES_API_PROFILE = {'name'}


def profile(request):
    """Fetches profile info"""
    session_id = request.cookies.get('session_id')
    if not session_id or not db.collection('sessions').document(
            session_id).get().exists:
        return jsonify({"error": "Not authenticated"}), 401

    prop = request.args.get('property', default='')

    if not prop in ALLOWED_PROPERTIES_API_PROFILE:
        return jsonify(error=f"'{prop}' is not a valid property."), 400

    value = ''
    doc = db.collection('sessions').document(session_id).get().to_dict()
    if 'profile' in doc:
        value = doc['profile'][prop]

    return jsonify(value=value)
