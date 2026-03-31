from features.users.repository import UserRepository
from features.users.model import User
from shared.auth import TokenClaims


class UserService:
    """Business logic layer for Users."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_profile_from_claims(self, claims: TokenClaims) -> dict:
        """Build a user profile dict directly from JWT claims (no DB call needed)."""
        return {
            "sub": claims.sub,
            "email": claims.email,
            "name": claims.name,
            "preferred_username": claims.preferred_username,
            "roles": claims.realm_access.roles,
        }

    def sync_user(self, claims: TokenClaims) -> User:
        """Upsert the Keycloak user into the local database."""
        return self.repository.upsert(
            keycloak_sub=claims.sub,
            email=claims.email or "",
            name=claims.name or "",
        )
