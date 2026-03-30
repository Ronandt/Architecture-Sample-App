from fastapi import APIRouter, Depends

from features.users.schemas import UserProfileResponse, UserSyncResponse
from features.users.repository import UserRepository
from features.users.service import UserService
from shared.dependencies import get_current_user

router = APIRouter(tags=["users"])


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)


@router.get("/me", response_model=UserProfileResponse)
def get_me(claims: dict = Depends(get_current_user)):
    """Return the current user's profile from JWT claims (no DB query)."""
    service = UserService(UserRepository())
    return service.get_profile_from_claims(claims)


@router.post("/sync", response_model=UserSyncResponse)
def sync_user(
    claims: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Upsert the authenticated Keycloak user into the local database."""
    return service.sync_user(claims)
