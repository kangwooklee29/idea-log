"""
gcp_app_engine/dao/__init__.py
"""

from .category_dao import CategoryDAO
from .message_dao import MessageDAO
from .user_dao import UserDAO

category_dao = CategoryDAO()
message_dao = MessageDAO()
user_dao = UserDAO()
