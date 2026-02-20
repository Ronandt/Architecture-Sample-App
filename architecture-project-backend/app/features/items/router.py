from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from model import ItemCreateRequest, ItemResponse
from service import ItemService
from infrastructure.adapters.keycloak_adapter import KeycloakAdapter
from fastapi_keycloak_middleware import KeycloakConfiguration
from schemas import ItemCreateRequest, ItemResponse
router = APIRouter()
keycloak = KeycloakAdapter()



@router.post("/items", response_model=ItemResponse)
def create_item(item_data: ItemCreateRequest, token=Depends(keycloak.get_current_user)):
    user_id = token[1]["sub"]
    return ItemService.create_item(item_data.dict(), user_id)


@router.get("/items", response_model=List[ItemResponse])
def get_items(token=Depends(keycloak.get_current_user)):
    user_id = token[1]["sub"]
    return ItemService.get_user_items(user_id)


@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, token=Depends(keycloak.get_current_user)):
    user_id = token[1]["sub"]
    return ItemService.get_item(item_id, user_id)
