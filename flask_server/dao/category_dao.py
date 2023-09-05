"""
flask_server/dao/category_dao.py
"""

from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError

from .base_dao import BaseDAO, db
from ..models import Category

DEFAULT_CATEGORIES = ['All', 'None', 'Deleted']


class CategoryDAO(BaseDAO):
    """
    Data access object (DAO) for Category operations.

    Provides methods for fetching, creating, checking, and updating categories related to users.

    Inherits:
        BaseDAO: Base class providing fundamental CRUD operations.

    Attributes:
        - None

    Methods:
        - fetch_by_user_id(user_id: str) -> List[Category]: 
            Fetch all categories associated with the given user ID.
        - create_categories_for_user(user_id: str) -> bool: 
            Create default categories for a given user ID.
        - check_if_joined(user_id: str) -> bool: 
            Check if a user has joined categories.
        - update_category(name: str, category_id: Optional[str], user_id: str) -> bool: 
            Update a category's name or create a new one for a user.
    """

    def fetch_by_user_id(self, user_id: str) -> List[Category]:
        """
        Fetch all categories associated with the specified user ID.

        Args:
            user_id (str): The user ID to fetch categories for.

        Returns:
            List[Category]: A list of Category objects associated with the user.
        """
        return Category.query.filter_by(user_id=user_id).all()

    def create_categories_for_user(self, user_id: str) -> bool:
        """
        Create default categories for a specific user ID.

        Args:
            user_id (str): The user ID for which to create default categories.

        Returns:
            bool: True if categories were successfully created, False otherwise.
        """
        try:
            result = False
            for category_name in DEFAULT_CATEGORIES:
                result |= self.save(
                    Category(name=category_name, user_id=user_id))
            return result
        except:
            db.session.rollback()
            return False

    def check_if_joined(self, user_id: str) -> bool:
        """
        Verify if a user has any associated categories.

        Args:
            user_id (str): The user ID to check for associated categories.

        Returns:
            bool: True if the user has categories, False otherwise.
        """
        try:
            return bool(
                db.session.query(Category).filter_by(user_id=user_id).first())
        except SQLAlchemyError:
            db.session.rollback()
            return False

    def update_category(self, name: str, category_id: Optional[str],
                        user_id: str) -> bool:
        """
        Update the name of a specific category or create a new one for the user 
        if no category ID is provided.

        Args:
            name (str): The new category name.
            category_id (Optional[str]): The ID of the category to update. If None, 
                                         a new category will be created.
            user_id (str): The user ID associated with the category.

        Returns:
            bool: True if the category was successfully updated or created, False otherwise.
        """
        if not category_id:
            return self.save(Category(name=name, user_id=user_id))
        category = Category.query.get(category_id)
        if not category:
            return False
        return self.update(category, name=name)
