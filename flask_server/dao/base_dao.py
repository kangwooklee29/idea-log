"""
flask_server/dao/base_dao.py
"""

from typing import Any

from ..models import db


class BaseDAO:
    """
    A base data access object (DAO) providing basic CRUD operations.

    This class offers methods to save, delete, and update entities 
    in the database using the Flask-SQLAlchemy session.

    Attributes:
        - None

    Methods:
        - save(entity: Any) -> bool: 
            Save a given entity to the database.
        - delete(entity: Any) -> bool: 
            Delete a given entity from the database.
        - update(entity: Any, **kwargs: Any) -> bool: 
            Update a given entity's attributes to the provided values.
    """

    def save(self, entity: Any) -> bool:
        """
        Save the provided entity to the database.

        Args:
            entity (Any): The entity to be saved.

        Returns:
            bool: True if the entity was saved successfully, False otherwise.
        """
        try:
            db.session.add(entity)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    def delete(self, entity: Any) -> bool:
        """
        Delete the provided entity from the database.

        Args:
            entity (Any): The entity to be deleted.

        Returns:
            bool: True if the entity was deleted successfully, False otherwise.
        """
        try:
            db.session.delete(entity)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    def update(self, entity: Any, **kwargs: Any) -> bool:
        """
        Update the attributes of the provided entity with the given values.

        Args:
            entity (Any): The entity whose attributes are to be updated.
            **kwargs (Any): Variable length argument list of attribute names 
                            and their corresponding values.

        Returns:
            bool: True if the entity was updated successfully, False otherwise.
        """
        try:
            for key, value in kwargs.items():
                setattr(entity, key, value)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
