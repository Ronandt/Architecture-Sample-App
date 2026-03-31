from pydantic import BaseModel, ConfigDict


class UserProfileResponse(BaseModel):
    sub: str
    email: str | None
    name: str | None
    preferred_username: str | None
    roles: list[str]


class UserSyncResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    keycloak_sub: str
    email: str | None
    name: str | None
