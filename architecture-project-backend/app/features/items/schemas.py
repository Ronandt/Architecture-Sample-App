from pydantic import BaseModel, Field



class ItemCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(None, max_length=500)

class ItemResponse(BaseModel):
    id: int
    title: str
    description: str = None
    owner_id: str

