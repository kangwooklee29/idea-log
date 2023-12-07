"""
gcp_app_engine/dao/__init__.py
"""

from .category_dao import CategoryDAO
from .message_dao import MessageDAO

category_dao = CategoryDAO()
message_dao = MessageDAO()
