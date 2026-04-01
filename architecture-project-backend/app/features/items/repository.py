import logging

from fastapi_sqlalchemy import db
from sqlalchemy.exc import SQLAlchemyError

from features.items.model import Item
from shared.exceptions import DatabaseUnavaliable, ItemNotFound

logger = logging.getLogger(__name__)


class ItemRepository:
    """Data access layer for Items."""

    def create_item(self, title: str, description: str, owner_id: str) -> Item:
        try:
            item = Item(title=title, description=description, owner_id=owner_id)
            db.session.add(item)
            db.session.commit()
            db.session.refresh(item)
            return item
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error on create_item: %s", e)
            raise DatabaseUnavaliable("Database has problems, try again")

    def get_items_for_user(self, owner_id: str) -> list[Item]:
        """Return all items belonging to a Keycloak user."""
        try:
            return db.session.query(Item).filter(Item.owner_id == owner_id).all()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error on get_items_for_user: %s", e)
            raise DatabaseUnavaliable("An unexpected database error occurred.")

    def get_item(self, item_id: int, owner_id: str) -> Item:
        """Return a single item by ID and owner, or raise ItemNotFound."""
        try:
            item = (
                db.session.query(Item)
                .filter(Item.id == item_id, Item.owner_id == owner_id)
                .first()
            )
            if not item:
                raise ItemNotFound(f"Item with ID {item_id} not found for this user.")
            return item
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error on get_item: %s", e)
            raise DatabaseUnavaliable("An unexpected database error occurred.")

    def update_image_url(self, item_id: int, owner_id: str, image_url: str) -> Item:
        """Persist the S3 image URL on the item row."""
        try:
            item = self.get_item(item_id, owner_id)
            item.image_url = image_url
            db.session.commit()
            db.session.refresh(item)
            return item
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error("Database error on update_image_url: %s", e)
            raise DatabaseUnavaliable("An unexpected database error occurred.")
