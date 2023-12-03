"""
gcp_cloud_functions/api/fetch_messages/main.py
"""

import firebase_admin  # pylint: disable=import-error
from firebase_admin import firestore  # pylint: disable=import-error
from flask import jsonify

if not firebase_admin._apps:
    firebase_admin.initialize_app()
db = firestore.client()


def fetch_messages(request):
    """Fetches messages for the request"""
    session_id = request.cookies.get('session_id')
    if not session_id or not db.collection('sessions').document(
            session_id).get().exists:
        return jsonify({"error": "Not authenticated"}), 401

    limit = request.args.get('limit', default='')
    parent_msg_id = request.args.get('parent_msg_id', default='')
    target_date = request.args.get('target_date', default='')
    category_id = request.args.get('category_id', default='')
    user_id = db.collection('sessions').document(
        session_id).get().to_dict()['profile']['id']

    # Get all messages for a particular parent
    if limit == "-1":
        query = db.collection('messages').where('parent_msg_id', '==',
                                                parent_msg_id).stream()
        messages = [doc.to_dict() for doc in query]
    # Infinite scroll: get a limited number of messages based on date and category
    elif limit == "20":
        name = db.collection('category').document(
            category_id).get().to_dict()['name']
        if name == 'All':
            category_query = db.collection('category').where(
                'user_id', '==', user_id).stream()
            query = db.collection('messages').where('user_id', '==', user_id)
            for category in category_query:
                name = category.to_dict()['name']
                if name == 'Deleted':
                    continue
                query = query.where('name', '==', name)
        else:
            query = db.collection('messages').where('category_id', '==',
                                                    category_id).where(
                                                        'parent_msg_id', '==',
                                                        -1)

        if target_date:
            query = query.where('written_date', '<', target_date)
        else:
            query = query.where('written_date', '>', 0)

        query = query.order_by(
            'written_date',
            direction=firestore.Query.DESCENDING).limit(20).stream()
        messages = [doc.to_dict() for doc in query]

    # Get the latest updated message
    else:
        query = db.collection('messages').where(
            'user_id', '==', user_id).order_by(
                'msg_id',
                direction=firestore.Query.DESCENDING).limit(1).stream()
        messages = [doc.to_dict() for doc in query]

    return jsonify(messages)
