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


    def fetch_by_user_id(self, user_id: str):
        """
        Fetch all options associated with the specified user ID.

        Args:
            user_id (str): The user ID to fetch options for.

        Returns:
            Dict: A dictionary of options associated with the user.
        """
        query = db.collection('user').where('user_id', '==',
                                            user_id).limit(1).get()
        for doc in query:
            if doc.exists:
                return doc.to_dict()
        return {}


    def update_by_user_id(self, **kwargs):
        """
        Update all options associated with the specified user ID.

        Args:
            **kwargs: data to update

        Returns:
            bool: True if succeed to update, False otherwise
        """
        user_id = kwargs.get('user_id')
        username = kwargs.get('username')
        api_key = kwargs.get('api_key')
        query = db.collection('user').where('user_id', '==',
                                            user_id).limit(1).get()
        for doc in query:
            if doc.exists:
                doc.reference.update({"username": username, "api_key": api_key})
                return True
        return False
