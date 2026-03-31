from fastapi import Depends

from features.items.repository import ItemRepository
from features.items.service import ItemService
from shared.dependencies import get_s3_client
from infrastructure.adapters.s3_adapter import S3BucketClient


def get_item_repository() -> ItemRepository:
    return ItemRepository()


def get_item_service(
    repo: ItemRepository = Depends(get_item_repository),
    s3: S3BucketClient = Depends(get_s3_client),
) -> ItemService:
    return ItemService(repo, s3_client=s3)
