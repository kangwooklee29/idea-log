"""
flask_server/models/category.py
"""

from typing import Dict, Any
from . import db


class Category(db.Model):
    """
    Represents a Category in the system.

    Attributes:
        id: The unique identifier for the category.
        name: The name of the category.
        user_id: The identifier for the user associated with the category.
    """
    # pylint: disable=too-few-public-methods
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    user_id = db.Column(db.String)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Category object into a dictionary.

        Returns:
            A dictionary representation of the Category object.
        """
        return {'id': self.id, 'user_id': self.user_id, 'name': self.name}
