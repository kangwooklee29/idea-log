"""
gcp_cloud_functions/api/update_category/main.py
"""

from urllib.parse import unquote
import firebase_admin  # pylint: disable=import-error
from firebase_admin import firestore  # pylint: disable=import-error
from flask import jsonify

if not firebase_admin._apps:
    firebase_admin.initialize_app()
db = firestore.client()


def update_category_in_db(name, category_id, user_id):
    """Updates category info in db"""
    if not category_id:
        query = db.collection('category').where('user_id', '==',
                                                user_id).stream()
        for doc in query:
            if doc.to_dict()['name'] == name:
                category_id = doc.reference.id
                break
        else:
            _, doc_ref = db.collection('category').add({
                'name': name,
                'user_id': user_id
            })
            category_id = doc_ref.id
        return category_id

    doc = db.collection('category').document(category_id).get()
    if not doc.exists:
        return False

    doc.reference.update({'name': name})
    return category_id


def update_category(request):
    """Updates category info"""
    session_id = request.cookies.get('session_id')
    if not session_id or not db.collection('sessions').document(
            session_id).get().exists:
        return jsonify({"error": "Not authenticated"}), 401

    name = unquote(request.args.get('name', default=''))
    category_id = request.args.get('id', default='')

    doc = db.collection('sessions').document(session_id).get().to_dict()
    updated_category_id = update_category_in_db(name, category_id,
                                                doc['profile']['id'])
    if updated_category_id:
        return jsonify(updated_category_id)
    return jsonify(success=False)
