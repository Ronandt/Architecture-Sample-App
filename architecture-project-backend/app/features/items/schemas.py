from pydantic import BaseModel, Field, ConfigDict


class ItemCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(None, max_length=500)


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    owner_id: str
    image_url: str | None = None

