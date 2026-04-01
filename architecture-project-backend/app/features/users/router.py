from typing import Annotated
from fastapi import APIRouter, Depends

from features.users.schemas import UserProfileResponse, UserSyncResponse
from features.users.service import UserService
from features.users.dependencies import get_user_service
from shared.dependencies import get_current_user, require_admin
from shared.auth import TokenClaims

router = APIRouter(tags=["users"], dependencies=[Depends(get_current_user)])


@router.get("/me", response_model=UserProfileResponse)
def get_me(
    claims: TokenClaims = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Return the current user's profile from JWT claims (no DB query)."""
    return service.get_profile_from_claims(claims)


@router.get("/all", response_model=list[UserSyncResponse], dependencies=[Depends(require_admin)])
def get_all_users(service: Annotated[UserService, Depends(get_user_service)]):
    """Return all users. Requires the configured admin role."""
    return service.get_all_users()


@router.post("/sync", response_model=UserSyncResponse)
def sync_user(
    claims: TokenClaims = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Upsert the authenticated Keycloak user into the local database."""
    return service.sync_user(claims)
