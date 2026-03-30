from __future__ import annotations

from features.items.repository import ItemRepository
from features.items.model import Item
from shared.exceptions import InvalidItemTitle, InvalidItemDescription, ItemUploadError


class ItemService:
    """Business logic layer for Items."""

    def __init__(self, repository: ItemRepository, s3_client=None):
        self.repository = repository
        self.s3_client = s3_client

    def create_item(self, title: str, description: str | None, keycloak_user_id: str) -> Item:
        sanitised_title = title.strip()
        sanitised_description = description.strip() if description else ""

        if len(sanitised_title) == 0:
            raise InvalidItemTitle("Title must have more than 0 characters")
        if len(sanitised_title) > 30:
            raise InvalidItemTitle("Title exceeds 30 characters")
        if len(sanitised_description) > 100:
            raise InvalidItemDescription("Description exceeds 100 characters")

        return self.repository.create_item(sanitised_title, sanitised_description, keycloak_user_id)

    def get_user_items(self, keycloak_user_id: str) -> list[Item]:
        return self.repository.get_items_for_user(keycloak_user_id)

    def get_item(self, item_id: int, keycloak_user_id: str) -> Item:
        return self.repository.get_item(item_id, keycloak_user_id)

    def upload_file(self, item_id: int, owner_id: str, filename: str, data: bytes, content_type: str) -> str:
        """Upload a file for an item and return a presigned URL (or the object URL)."""
        if self.s3_client is None:
            raise ItemUploadError("File uploads are not configured on this server")
        if not filename:
            raise ItemUploadError("Filename must not be empty")

        # Verify the item belongs to this user before uploading
        self.repository.get_item(item_id, owner_id)

        object_key = f"items/{owner_id}/{item_id}/{filename}"
        url = self.s3_client.upload(object_key, data, content_type=content_type)
        presigned = self.s3_client.generate_presigned_url(url)
        return presigned or url
