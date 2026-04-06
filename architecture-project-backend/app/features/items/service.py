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

    def create_item(
        self, title: str, description: str | None, keycloak_user_id: str
    ) -> ItemResponse:
        sanitised_title = title.strip()
        sanitised_description = description.strip() if description else ""

        if len(sanitised_title) == 0:
            raise InvalidItemTitle("Title must have more than 0 characters")
        if len(sanitised_title) > 30:
            raise InvalidItemTitle("Title exceeds 30 characters")
        if len(sanitised_description) > 100:
            raise InvalidItemDescription("Description exceeds 100 characters")

        item = self.repository.create_item(
            sanitised_title, sanitised_description, keycloak_user_id
        )
        return self._resolve(item)

    def upload_file(
        self, item_id: int, owner_id: str, filename: str, data: bytes, content_type: str
    ) -> str:
        """Upload a file for an item, persist the object key, and return a presigned URL."""
        if self.s3_client is None:
            raise ItemUploadError("File uploads are not configured on this server")
        if not filename:
            raise ItemUploadError("Filename must not be empty")

        self.s3_client.ping()

        item = self.repository.get_item(item_id, owner_id)

        object_key = f"items/{owner_id}/{item_id}/{filename}"
        if item.image_url and item.image_url != object_key:
            self.s3_client.delete(item.image_url)

        self.s3_client.upload(object_key, data, content_type=content_type)
        self.repository.update_image_url(item_id, owner_id, object_key)

        return self.s3_client.generate_presigned_url(object_key)

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def get_user_items(self, keycloak_user_id: str) -> list[ItemResponse]:
        return [
            self._resolve(item)
            for item in self.repository.get_items_for_user(keycloak_user_id)
        ]

    def get_item(self, item_id: int, keycloak_user_id: str) -> ItemResponse:
        return self._resolve(self.repository.get_item(item_id, keycloak_user_id))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve(self, item: Item) -> ItemResponse:
        """Resolve the stored object key to a fresh presigned URL."""
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
