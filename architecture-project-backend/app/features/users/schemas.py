from pydantic import BaseModel


class UserProfileResponse(BaseModel):
    sub: str
    email: str | None
    name: str | None
    preferred_username: str | None
    roles: list[str]


class UserSyncResponse(BaseModel):
    id: int
    keycloak_sub: str
    email: str | None
    name: str | None

    class Config:
        from_attributes = True
