from fastapi_sqlalchemy import db
from items import Item
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DatabaseError, OperationalError
from shared.exceptions import DatabaseUnavaliable, ItemNotFound

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
        except OperationalError as e:
            db.session.rollback()
            print(f"An unexpected SQLAlchemy error occurred: {e}")
            raise DatabaseUnavaliable("Database has problems, try again")


    @staticmethod
    def get_items_for_user(owner_id: str):
        """Get all items belonging to a Keycloak user."""
        try:
            items = db.session.query(Item).filter(Item.owner_id == owner_id).all()
            return items

        except OperationalError as e:
            db.session.rollback()
            print(f"Unexpected database error: {e}")
            raise DatabaseUnavaliable("An unexpected database error occurred.")

    @staticmethod
    def get_item(item_id: int, owner_id: str):
        """Get a single item by ID and owner."""
        try:
            item = (
                db.session.query(Item)
                .filter(Item.id == item_id, Item.owner_id == owner_id)
                .first()
            )
            if not item:
                raise ItemNotFound(f"Item with ID {item_id} not found for this user.")
            return item

        except OperationalError as e:
            db.session.rollback()
            print(f"Unexpected database error: {e}")
            raise DatabaseUnavaliable("An unexpected database error occurred.")