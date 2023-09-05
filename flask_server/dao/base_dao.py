from typing import Any, Dict

from ..models import db

class BaseDAO:

    def save(self, entity: Any) -> bool:
        try:
            db.session.add(entity)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    def delete(self, entity: Any) -> bool:
        try:
            db.session.delete(entity)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False

    def update(self, entity: Any, **kwargs: Dict[str, Any]) -> bool:
        try:
            for key, value in kwargs.items():
                setattr(entity, key, value)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
