"""
gcp_app_engine/dao/user_dao.py
"""

from .base_dao import db


class UserDAO():
    """
    Data access object (DAO) for User operations.

    Provides methods for fetching, creating, checking, and updating user info.

    Attributes:
        - None
    
    Methods:
        - assign_username(user_id: str, username: str) -> bool: 
            Assign the user name to the given user ID.
    """

    def assign_username(self, user_id: str, username: str) -> bool:
        """
        Assign the user name to the given user ID.

        Args:
            user_id (str): The user id for which to assign.
            username (str): The user name for which to assign.

        Returns:
            bool: True if the user name were successfully assgined, False otherwise.
        """
        try:
            result = db.collection('user').where('user_id', '==',
                                                 user_id).limit(1).stream()
            doc = next(result, None)
            if doc is not None:
                doc.reference.update({"username": username})
            else:
                db.collection('user').add({
                    'user_id': user_id,
                    'username': username
                })

            return True
        except:
            return False
