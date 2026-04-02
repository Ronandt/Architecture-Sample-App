from typing import List

from fastapi import APIRouter, Depends, UploadFile, File

from features.items.schemas import ItemCreateRequest, ItemResponse, ItemUploadResponse
from features.items.service import ItemService
from features.items.dependencies import get_item_service
from shared.dependencies import get_current_user
from shared.schemas import TokenClaims

router = APIRouter(tags=["items"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=ItemResponse, status_code=201)
def create_item(
    item_data: ItemCreateRequest,
    claims: TokenClaims = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    return service.create_item(item_data.title, item_data.description, claims.sub)


@router.get("", response_model=List[ItemResponse])
def get_items(
    claims: TokenClaims = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    return service.get_user_items(claims.sub)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    claims: TokenClaims = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    return service.get_item(item_id, claims.sub)


@router.post("/{item_id}/upload", response_model=ItemUploadResponse)
async def upload_item_file(
    item_id: int,
    file: UploadFile = File(...),
    claims: TokenClaims = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    data = await file.read()
    url = service.upload_file(item_id, claims.sub, file.filename, data, file.content_type)
    return ItemUploadResponse(url=url)
