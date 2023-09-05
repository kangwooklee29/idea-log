"""
flask_server/models/message.py
"""

from typing import Dict, Any
from . import db


class Message(db.Model):
    """
    Represents a Message in the system.

    Attributes:
        msg_id: The unique identifier for the message.
        category_id: The identifier for the message's category.
        written_date: The date when the message was written.
        message: The content of the message.
        user_id: The identifier for the user who wrote the message.
        parent_msg_id: The identifier for the parent message (for threaded messages).
    """
    # pylint: disable=too-few-public-methods
    msg_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer)
    written_date = db.Column(db.Integer)
    message = db.Column(db.String)
    user_id = db.Column(db.String)
    parent_msg_id = db.Column(db.Integer)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Message object into a dictionary.

        Returns:
            A dictionary representation of the Message object.
        """
        return {
            'msg_id': self.msg_id,
            'parent_msg_id': self.parent_msg_id,
            'written_date': self.written_date,
            'message': self.message,
            'category_id': self.category_id,
            'user_id': self.user_id
        }
