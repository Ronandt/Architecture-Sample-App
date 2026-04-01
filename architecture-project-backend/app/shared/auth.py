from pydantic import BaseModel


class RealmAccess(BaseModel):
    roles: list[str] = []


class TokenClaims(BaseModel):
    sub: str
    email: str | None = None
    name: str | None = None
    preferred_username: str | None = None
    realm_access: RealmAccess = RealmAccess()
    groups: list[str] = []
