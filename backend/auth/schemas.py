from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    exp: datetime


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class TokensResponse(Tokens):
    token_type: Literal["bearer"]
