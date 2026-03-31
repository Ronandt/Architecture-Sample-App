from features.users.repository import UserRepository
from features.users.schemas import UserProfileResponse, UserSyncResponse
from shared.auth import TokenClaims


class UserService:
    """Business logic layer for Users."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_profile_from_claims(self, claims: TokenClaims) -> UserProfileResponse:
        """Build a user profile directly from JWT claims (no DB call needed)."""
        return UserProfileResponse(
            sub=claims.sub,
            email=claims.email,
            name=claims.name,
            preferred_username=claims.preferred_username,
            roles=claims.realm_access.roles,
        )

    def sync_user(self, claims: TokenClaims) -> UserSyncResponse:
        """Upsert the Keycloak user into the local database."""
        user = self.repository.upsert(
            keycloak_sub=claims.sub,
            email=claims.email or "",
            name=claims.name or "",
        )
        return UserSyncResponse.model_validate(user)
