from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.param_functions import Form

from auth.auth_exceptions import UnAuthorized
from auth.jwt_class import Jwt
from settings import settings


auth_jwt = Jwt()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    payload = auth_jwt.verify_token(token)
    username = payload.sub

    if not username:
        raise UnAuthorized()

    return username


class OAuth2UserAuthForm(OAuth2PasswordRequestForm):
    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password"),
        email: str = Form(),
        password: str = Form(),
        scope: str = Form(default=""),
        client_id: Optional[str] = Form(default=None),
        client_secret: Optional[str] = Form(default=None),
    ):
        super().__init__(
            grant_type=grant_type,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
            username=email,
        )
        self.email = email
