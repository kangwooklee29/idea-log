"""
gcp_app_engine/dao/message_dao.py
"""

from typing import Optional
from firebase_admin import firestore  # pylint: disable=import-error
from flask import jsonify, Response
from .base_dao import db


class MessageDAO():
    """
    Data access object (DAO) for Message operations.

    Provides methods for writing and fetching messages associated with users and categories.

    Attributes:
        - None

    Methods:
        - write_message(message: str, written_date: str, category_id: str,
                        msg_id: Optional[str], user_id: str) -> bool:
            Write or update a message with the provided parameters.
        - fetch_messages(target: str, limit: str, parent_msg_id: int,
                         target_date: Optional[str], category_id: str,
                         user_id: int) -> Response:
            Fetch messages based on various filtering criteria.
    """

    def write_message(self, data) -> bool:
        """
        Write or update a message with the specified parameters.

        Args:
            data: a Dict which has keys such as category_id, written_date, message, msg_id

        Returns:
            bool: True if the message was successfully written or updated, False otherwise.
        """
        usr_msg_col_ref = db.collection('messages')
        if 'msg_id' not in data:
            usr_msg_col_ref.add({
                'category_id': data['category_id'],
                'written_date': data['written_date'],
                'message': data['message'],
                'user_id': data['user_id'],
            })
        else:
            target_to_modify = usr_msg_col_ref.document(data['msg_id']).get()
            modified_dict = target_to_modify.to_dict()

            if 'category_id' in data:
                modified_dict['category_id'] = data['category_id']
            if 'message' in data:
                modified_dict['message'] = data['message']

            category_name = db.collection('category').document(
                modified_dict['category_id']).get().to_dict()['name']
            if category_name == 'Deleted':
                target_to_modify.reference.delete()
                db.collection('deleted_messages').add(modified_dict)
            else:
                target_to_modify.reference.update(modified_dict)

        return True

    def fetch_messages(self, **kwargs) -> Response:
        """
        Fetch messages based on various filtering criteria.

        Args:
            limit (str): Limit for the number of messages to be retrieved.
            parent_msg_id (int): ID of the parent message; used to fetch replies.
            target_date (Optional[str]): Date threshold for fetching messages.
            category_id (str): ID of the associated category.

        Returns:
            Response: A Flask Response object containing a list of message dicts in JSON format.
        """
        limit: Optional[str] = kwargs.get('limit')
        parent_msg_id: Optional[int] = kwargs.get('parent_msg_id')
        target_date: Optional[str] = kwargs.get('target_date')
        category_id: Optional[str] = kwargs.get('category_id')
        user_id: Optional[str] = kwargs.get('user_id')

        category_name = db.collection('category').document(
            category_id).get().to_dict()['name']
        if category_name == 'Deleted':
            query = db.collection('deleted_messages')
        else:
            query = db.collection('messages')

        # Get all messages for a particular parent
        if limit == "-1":
            query = db.collection('comments').where('parent_msg_id', '==',
                                                    parent_msg_id).stream()
        # Infinite scroll: get a limited number of messages based on date and category
        elif limit == "20":
            if category_name == 'All':
                query = query.where('user_id', '==', user_id)
            else:
                query = query.where('category_id', '==', category_id)

            if target_date:
                query = query.where('written_date', '<', int(target_date))
            else:
                query = query.where('written_date', '>', 0)

            query = query.order_by(
                'written_date',
                direction=firestore.Query.DESCENDING).limit(20).stream()

        # Get the latest updated message
        else:
            query = query.where('category_id', '==', category_id) \
                .where('written_date', '>', 0).order_by(
                    'written_date',
                    direction=firestore.Query.DESCENDING).limit(1).stream()

        return jsonify([{'msg_id': doc.id, **doc.to_dict()} for doc in query])
