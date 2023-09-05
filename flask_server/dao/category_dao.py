from .base_dao import BaseDAO, db
from ..models import Category
from sqlalchemy.exc import SQLAlchemyError

DEFAULT_CATEGORIES = ['All', 'None', 'Deleted']

class CategoryDAO(BaseDAO):

    def fetch_by_user_id(self, user_id):
        return Category.query.filter_by(user_id=user_id).all()

    def create_categories_for_user(self, user_id):
        try:
            for category_name in DEFAULT_CATEGORIES:
                self.save(Category(name=category_name, user_id=user_id))
            return True
        except:
            db.session.rollback()
            return False

    def check_if_joined(self, user_id):
        try:        
            if db.session.query(Category).filter_by(user_id=user_id).first():
                return True
            else:
                return False
        except SQLAlchemyError:
            db.session.rollback()
            return False

    def update_category(self, name, category_id, user_id):
        if not category_id:
            return self.save(Category(name=name, user_id=user_id))
        else:
            category = Category.query.get(category_id)
        if not category:
            return False
        return self.update(category, name=name)
