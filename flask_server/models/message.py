from . import db

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
