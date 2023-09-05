from typing import Optional, Union, Any

from .base_dao import BaseDAO, db
from flask import jsonify, Response
from ..models import Message

class MessageDAO(BaseDAO):

    def write_message(self, message: str, written_date: str, category_id: str, msg_id: Optional[str], user_id: str) -> bool:
        try:
            if not msg_id:
                new_message = Message(
                    category_id=category_id,
                    user_id=user_id,
                    parent_msg_id=-1,
                    written_date=written_date,
                    message=message
                )
                self.save(new_message)

            else:
                target_to_modify = Message.query.filter_by(msg_id=msg_id).first()
                if target_to_modify.category_id == category_id:
                    self.update(target_to_modify,
                                user_id=user_id,
                                parent_msg_id=-1,
                                written_date=written_date,
                                message=message)
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
            return False

    def fetch_messages(self, target: str, limit: str, parent_msg_id: int, target_date: Optional[str], category_id: str, user_id: int) -> Response:
        # Get all messages for a particular parent
        if limit == "-1":
            messages = Message.query.filter_by(parent_msg_id=parent_msg_id).all()
        # Infinite scroll: get a limited number of messages based on date and category
        elif limit == "20":
            query = Message.query.filter_by(parent_msg_id=-1, user_id=user_id)

            if target_date:
                query = query.filter(Message.written_date < target_date)

            if category_id == "1":
                query = query.filter(Message.category_id != 3)
            else:
                query = query.filter_by(category_id=category_id)

            messages = query.order_by(Message.written_date.desc()).limit(20).all()
        # Get the latest updated message
        else:
            messages = Message.query.filter_by(user_id=user_id).order_by(Message.msg_id.desc()).limit(1).all()

        return jsonify([msg.to_dict() for msg in messages])
