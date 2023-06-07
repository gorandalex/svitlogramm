from .core import CoreModel


class TokenResponse(CoreModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    