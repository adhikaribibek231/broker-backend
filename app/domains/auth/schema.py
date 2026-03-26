from pydantic import BaseModel

class RefreshTokenIn(BaseModel):
    refresh_token: str