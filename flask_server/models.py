from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

DEFAULT_CATEGORIES = ['All', 'None', 'Deleted']

db = SQLAlchemy()

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    user_id = db.Column(db.String)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name
        }

class Message(db.Model):
    msg_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer)
    written_date = db.Column(db.Integer)
    message = db.Column(db.String)
    user_id = db.Column(db.String)
    parent_msg_id = db.Column(db.Integer)

    def to_dict(self):
        return {
            'msg_id': self.msg_id,
            'parent_msg_id': self.parent_msg_id,
            'written_date': self.written_date,
            'message': self.message,
            'category_id': self.category_id,
            'user_id': self.user_id
        }

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

def fetch_categories(user_id):
    return Category.query.filter_by(user_id=user_id).all()

def write_message(message, written_date, category_id, msg_id):
    try:
        if not msg_id:
            new_message = Message(
                category_id=category_id,
                user_id=user_id,
                parent_msg_id=-1,
                written_date=written_date,
                message=message
            )
            db.session.add(new_message)

        else:
            target_to_modify = Message.query.filter_by(msg_id=msg_id).first()
            if target_to_modify.category_id == category_id:
                target_to_modify.user_id = user_id
                target_to_modify.parent_msg_id = parent_msg_id
                target_to_modify.written_date = written_date
                target_to_modify.message = message
            else:
                queue = [msg_id]
                target_to_modify.parent_msg_id = -1
                s, e = 0, 0
                while s <= e:
                    current_message = Message.query.filter_by(msg_id=queue[s]).first()
                    current_message.category_id = category_id
                    replies = Message.query.filter_by(parent_msg_id=queue[s]).all()
                    e += len(replies)
                    for reply in replies:
                        queue.append(reply.msg_id)
                    s += 1

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {e}")
        return f"Operation failed: {e}", 500
