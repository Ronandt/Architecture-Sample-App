from typing import List

from fastapi import APIRouter, Depends, UploadFile, File

from features.items.schemas import ItemCreateRequest, ItemResponse
from features.items.service import ItemService
from shared.dependencies import get_current_user, get_item_service

router = APIRouter(tags=["items"])


@router.post("", response_model=ItemResponse, status_code=201)
def create_item(
    item_data: ItemCreateRequest,
    claims: dict = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    return service.create_item(item_data.title, item_data.description, claims["sub"])


@router.get("", response_model=List[ItemResponse])
def get_items(
    claims: dict = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    return service.get_user_items(claims["sub"])


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    claims: dict = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    return service.get_item(item_id, claims["sub"])


@router.post("/{item_id}/upload")
async def upload_item_file(
    item_id: int,
    file: UploadFile = File(...),
    claims: dict = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    data = await file.read()
    url = service.upload_file(item_id, claims["sub"], file.filename, data, file.content_type)
    return {"url": url}
