from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

DEFAULT_CATEGORIES = ['All', 'None', 'Deleted']

db = SQLAlchemy()

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    user_id = db.Column(db.String)

class Message(db.Model):
    msg_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer)
    written_date = db.Column(db.Integer)
    message = db.Column(db.String)
    user_id = db.Column(db.String)
    parent_msg_id = db.Column(db.Integer)

def create_categories_for_user(user_id):
    try:
        for category_name in DEFAULT_CATEGORIES:
            db.session.add(Category(name=category_name, user_id=user_id))
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False

def check_if_joined(user_id):
    try:        
        if db.session.query(Category).filter_by(user_id=user_id).first():
            return True
        else:
            return False
    except NoResultFound:
        return False
    except SQLAlchemyError:
        db.session.rollback()
        return False
