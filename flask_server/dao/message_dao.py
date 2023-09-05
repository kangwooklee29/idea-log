"""
flask_server/dao/message_dao.py
"""

from typing import Optional
from flask import jsonify, Response

from .base_dao import BaseDAO, db
from ..models import Message


class MessageDAO(BaseDAO):
    """
    Data access object (DAO) for Message operations.

    Provides methods for writing and fetching messages associated with users and categories.

    Inherits:
        BaseDAO: Base class providing fundamental CRUD operations.

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

    def write_message(self, **kwargs) -> bool:
        """
        Write or update a message with the specified parameters.

        Args:
            message (str): Content of the message.
            written_date (str): Date when the message was written.
            category_id (str): ID of the associated category.
            msg_id (Optional[str]): Message ID to update; if None, a new message will be created.
            user_id (str): ID of the user associated with the message.

        Returns:
            bool: True if the message was successfully written or updated, False otherwise.
        """
        message: Optional[str] = kwargs.get('message')
        written_date: Optional[str] = kwargs.get('written_date')
        category_id: Optional[str] = kwargs.get('category_id')
        msg_id: Optional[str] = kwargs.get('msg_id')
        user_id: Optional[str] = kwargs.get('user_id')

        try:
            if not msg_id:
                self.save(
                    Message(category_id=category_id,
                            user_id=user_id,
                            parent_msg_id=-1,
                            written_date=written_date,
                            message=message))

            else:
                target_to_modify = Message.query.filter_by(
                    msg_id=msg_id).first()
                if target_to_modify.category_id == category_id:
                    self.update(target_to_modify,
                                user_id=user_id,
                                parent_msg_id=-1,
                                written_date=written_date,
                                message=message)
                else:
                    queue = [msg_id]
                    target_to_modify.parent_msg_id = -1
                    start, end = 0, 0
                    while start <= end:
                        current_message = Message.query.filter_by(
                            msg_id=queue[start]).first()
                        current_message.category_id = category_id
                        replies = Message.query.filter_by(
                            parent_msg_id=queue[start]).all()
                        end += len(replies)
                        for reply in replies:
                            queue.append(reply.msg_id)
                        start += 1
                    db.session.commit()

            return True

        except Exception as error_message:
            db.session.rollback()
            print(f"Error occurred: {error_message}")
            return False

    def fetch_messages(self, **kwargs) -> Response:
        """
        Fetch messages based on various filtering criteria.

        Args:
            target (str): Target type for the fetch operation.
            limit (str): Limit for the number of messages to be retrieved.
            parent_msg_id (int): ID of the parent message; used to fetch replies.
            target_date (Optional[str]): Date threshold for fetching messages.
            category_id (str): ID of the associated category.
            user_id (int): ID of the user associated with the messages.

        Returns:
            Response: A Flask Response object containing a list of message dicts in JSON format.
        """
        target: Optional[str] = kwargs.get('target')
        limit: Optional[str] = kwargs.get('limit')
        parent_msg_id: Optional[int] = kwargs.get('parent_msg_id')
        target_date: Optional[str] = kwargs.get('target_date')
        category_id: Optional[str] = kwargs.get('category_id')
        user_id: Optional[int] = kwargs.get('user_id')

        # Get all messages for a particular parent
        if limit == "-1":
            messages = Message.query.filter_by(
                parent_msg_id=parent_msg_id).all()
        # Infinite scroll: get a limited number of messages based on date and category
        elif limit == "20":
            query = Message.query.filter_by(parent_msg_id=-1, user_id=user_id)

            if target_date:
                query = query.filter(Message.written_date < target_date)

            if category_id == "1":
                query = query.filter(Message.category_id != 3)
            else:
                query = query.filter_by(category_id=category_id)

            messages = query.order_by(
                Message.written_date.desc()).limit(20).all()
        # Get the latest updated message
        else:
            messages = Message.query.filter_by(user_id=user_id).order_by(
                Message.msg_id.desc()).limit(1).all()

        return jsonify([msg.to_dict() for msg in messages])
