"""
gcp_app_engine/dao/category_dao.py
"""

from typing import List, Dict, Optional
from .base_dao import db

DEFAULT_CATEGORIES = ['All', 'None', 'Deleted']


class CategoryDAO():
    """
    Data access object (DAO) for Category operations.

    Provides methods for fetching, creating, checking, and updating categories related to users.

    Attributes:
        - None

    Methods:
        - fetch_by_user_id(user_id: str) -> List[Dict]: 
            Fetch all categories associated with the given user ID.
        - create_categories_for_user(user_id: str) -> bool: 
            Create default categories for a given user ID.
        - check_if_joined(user_id: str) -> bool: 
            Check if a user has joined categories.
        - update_category(name: str, category_id: Optional[str], user_id: str) -> bool: 
            Update a category's name or create a new one for a user.
    """

    def fetch_by_user_id(self, user_id: str) -> List[Dict]:
        """
        Fetch all categories associated with the specified user ID.

        Args:
            user_id (str): The user ID to fetch categories for.

        Returns:
            List[Dict]: A list of Category objects associated with the user.
        """
        query = db.collection('category').where('user_id', '==',
                                                user_id).stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in query]

    def create_categories_for_user(self, user_id: str) -> bool:
        """
        Create default categories for a specific user ID.

        Args:
            user_id (str): The user ID for which to create default categories.

        Returns:
            bool: True if categories were successfully created, False otherwise.
        """
        try:
            for category_name in DEFAULT_CATEGORIES:
                db.collection('category').add({
                    'name': category_name,
                    'user_id': user_id
                })
            return True
        except:
            return False

    def check_if_joined(self, user_id: str) -> bool:
        """
        Verify if a user has any associated categories.

        Args:
            user_id (str): The user ID to check for associated categories.

        Returns:
            bool: True if the user has categories, False otherwise.
        """
        result = db.collection('category').where('user_id', '==',
                                                 user_id).limit(1).stream()
        return next(result, None) is not None

    def update_category(self, name: str, category_id: Optional[str],
                        user_id: str) -> Optional[str]:
        """
        Update the name of a specific category or create a new one for the user 
        if no category ID is provided.

        Args:
            name (str): The new category name.
            category_id (Optional[str]): The ID of the category to update. If None, 
                                         a new category will be created.
            user_id (str): The user ID associated with the category.

        Returns:
            Optional[str]: category ID if the category was successfully updated or created, "" otherwise.
        """
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
            return ""

        doc.reference.update({'name': name})
        return category_id
