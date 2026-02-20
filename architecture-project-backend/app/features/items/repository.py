from fastapi_sqlalchemy import db
from items import Item
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DatabaseError
from shared.exceptions import ItemExists

class ItemRepository:
    """Handles DB queries for Items."""

    @staticmethod
    def create_item(title: str, description: str, owner_id: str) -> Item:
        try:
            item = Item(title=title, description=description, owner_id=owner_id)
            db.session.add(item)
            db.session.commit()
            db.session.refresh(item)
            return item
        except IntegrityError as e:
            db.session.rollback() 
            print(f"Data integrity error: {e.orig}")
            raise ItemExists("Item already exists")
         
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"An unexpected SQLAlchemy error occurred: {e}")
            raise DatabaseError("Database has problems, try again")


    @staticmethod
    def get_items_for_user(owner_id: str):
        return db.session.query(Item).filter(Item.owner_id == owner_id).all()

    @staticmethod
    def get_item(item_id: int, owner_id: str):
        return (
            db.session.query(Item)
            .filter(Item.id == item_id, Item.owner_id == owner_id)
            .first()
        )