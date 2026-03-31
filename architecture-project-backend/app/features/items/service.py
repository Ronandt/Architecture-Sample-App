from __future__ import annotations

from features.items.repository import ItemRepository
from features.items.model import Item
from features.items.schemas import ItemResponse
from shared.exceptions import InvalidItemTitle, InvalidItemDescription, ItemUploadError


class ItemService:
    """Business logic layer for Items."""

    def __init__(self, repository: ItemRepository, s3_client=None):
        self.repository = repository
        self.s3_client = s3_client

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def create_item(self, title: str, description: str | None, keycloak_user_id: str) -> ItemResponse:
        sanitised_title = title.strip()
        sanitised_description = description.strip() if description else ""

        if len(sanitised_title) == 0:
            raise InvalidItemTitle("Title must have more than 0 characters")
        if len(sanitised_title) > 30:
            raise InvalidItemTitle("Title exceeds 30 characters")
        if len(sanitised_description) > 100:
            raise InvalidItemDescription("Description exceeds 100 characters")

        item = self.repository.create_item(sanitised_title, sanitised_description, keycloak_user_id)
        return self._to_response(item)

    def upload_file(self, item_id: int, owner_id: str, filename: str, data: bytes, content_type: str) -> str:
        """Upload a file for an item, persist the object key, and return a presigned URL."""
        if self.s3_client is None:
            raise ItemUploadError("File uploads are not configured on this server")
        if not filename:
            raise ItemUploadError("Filename must not be empty")

        # Verify the item belongs to this user before uploading
        self.repository.get_item(item_id, owner_id)

        object_key = f"items/{owner_id}/{item_id}/{filename}"
        self.s3_client.upload(object_key, data, content_type=content_type)
        self.repository.update_image_url(item_id, owner_id, object_key)

        presigned = self.s3_client.generate_presigned_url(object_key)
        if presigned is None:
            raise ItemUploadError("Upload succeeded but could not generate a presigned URL")
        return presigned

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def get_user_items(self, keycloak_user_id: str) -> list[ItemResponse]:
        items = self.repository.get_items_for_user(keycloak_user_id)
        return [self._to_response(item) for item in items]

    def get_item(self, item_id: int, keycloak_user_id: str) -> ItemResponse:
        item = self.repository.get_item(item_id, keycloak_user_id)
        return self._to_response(item)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _to_response(self, item: Item) -> ItemResponse:
        """Convert an ORM Item to ItemResponse, swapping the stored object key for a presigned URL."""
        image_url: str | None = None
        if item.image_url and self.s3_client:
            image_url = self.s3_client.generate_presigned_url(item.image_url)
        return ItemResponse(
            id=item.id,
            title=item.title,
            description=item.description,
            owner_id=item.owner_id,
            image_url=image_url,
        )
