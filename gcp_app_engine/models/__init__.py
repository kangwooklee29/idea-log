"""
gcp_app_engine/models/__init__.py
"""

import firebase_admin  # pylint: disable=import-error
from firebase_admin import firestore  # pylint: disable=import-error

if not firebase_admin._apps:
    firebase_admin.initialize_app()
db = firestore.client()
