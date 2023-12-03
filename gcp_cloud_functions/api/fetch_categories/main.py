"""
gcp_cloud_functions/api/fetch_categories/main.py
"""

import firebase_admin  # pylint: disable=import-error
from firebase_admin import firestore  # pylint: disable=import-error
from flask import jsonify

if not firebase_admin._apps:
    firebase_admin.initialize_app()
db = firestore.client()


def fetch_categories(request):
    """Fetches categories for the authenticated user"""
    session_id = request.cookies.get('session_id')
    if not session_id or not db.collection('sessions').document(
            session_id).get().exists:
        return jsonify({"error": "Not authenticated"}), 401

    doc = db.collection('sessions').document(session_id).get().to_dict()
    query = db.collection('category').where('user_id', '==',
                                            doc['profile']['id']).stream()
    return jsonify([{'id': doc.id, **doc.to_dict()} for doc in query])
