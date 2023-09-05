from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .category import Category
from .message import Message
