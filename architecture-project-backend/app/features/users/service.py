from features.users.repository import UserRepository
from features.users.model import User


class UserService:
    """Business logic layer for Users."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_profile_from_claims(self, claims: dict) -> dict:
        """Build a user profile dict directly from JWT claims (no DB call needed)."""
        return {
            "sub": claims.get("sub"),
            "email": claims.get("email"),
            "name": claims.get("name"),
            "preferred_username": claims.get("preferred_username"),
            "roles": claims.get("realm_access", {}).get("roles", []),
        }

    def sync_user(self, claims: dict) -> User:
        """Upsert the Keycloak user into the local database."""
        return self.repository.upsert(
            keycloak_sub=claims["sub"],
            email=claims.get("email", ""),
            name=claims.get("name", ""),
        )
