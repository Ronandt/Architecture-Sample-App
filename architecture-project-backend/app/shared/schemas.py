from pydantic import BaseModel


class RoleAccess(BaseModel):
    roles: list[str] = []


class TokenClaims(BaseModel):
    sub: str
    email: str | None = None
    name: str | None = None
    preferred_username: str | None = None
    realm_access: RoleAccess = RoleAccess()
    resource_access: dict[str, RoleAccess] = {}
    groups: list[str] = []

    def get_client_roles(self, client_id: str) -> list[str]:
        """Return roles assigned to the user for a specific client."""
        return self.resource_access.get(client_id, RoleAccess()).roles
