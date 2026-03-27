from pydantic import BaseModel


class PropertyResponse(BaseModel):
    id: int
    title: str
    location: str
    price: int
    property_type: str
    image_url: str
    description: str
    is_active: bool

    model_config = {"from_attributes": True}