"""
gcp_cloud_functions/api/write_message/main.py
"""

import firebase_admin  # pylint: disable=import-error
from firebase_admin import firestore  # pylint: disable=import-error
from flask import jsonify

if not firebase_admin._apps:
    firebase_admin.initialize_app()
db = firestore.client()


def write_message(request):
    """Writes a new message"""
    session_id = request.cookies.get('session_id')
    if not session_id or not db.collection('sessions').document(
            session_id).get().exists:
        return jsonify({"error": "Not authenticated"}), 401

    doc = db.collection('sessions').document(session_id).get().to_dict()
    data = request.json

    if 'msg_id' not in data:
        db.collection('messages').add({
            'category_id': data['category_id'],
            'written_date': data['written_date'],
            'message': data['message'],
        })
    else:
        update_dict = {}
        if 'category_id' in data:
            update_dict['category_id'] = data['category_id']
        if 'message' in data:
            update_dict['message'] = data['message']

        target_to_modify = db.collection('messages').document(
            data['msg_id']).get()
        target_to_modify.reference.update(update_dict)

    return jsonify(success=True)
