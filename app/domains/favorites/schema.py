from datetime import datetime

from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    property_id: int


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    property_id: int
    created_at: datetime

    model_config = {"from_attributes": True}