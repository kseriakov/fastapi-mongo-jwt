from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from .schemas import Tokens, TokenPayload
from .auth_exceptions import UnAuthorized
from settings import settings


class Jwt:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(
        self,
        secret_key: str = settings.SECRET_KEY,
        algorithm: str = settings.ALGORITHM,
        access_token_lifetime: timedelta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
        refresh_token_lifetime: timedelta = timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        ),
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    def create_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + self.access_token_lifetime
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm
        )
        return encoded_jwt

    def create_tokens(self, data: dict) -> Tokens:
        access_token = self.create_token(data)
        refresh_token = self.create_token(data)
        return Tokens(access_token=access_token, refresh_token=refresh_token)

    def refresh_tokens(self, refresh_token: str, data: dict) -> Tokens:
        self.verify_token(refresh_token)
        return self.create_tokens(data)

    def get_tokens(
        self, username: str, plain_password: str, hashed_password: str
    ) -> Tokens:

        if not self.verify_password(plain_password, hashed_password):
            raise UnAuthorized(message="Password is wrong")

        data = {"sub": username}

        return self.create_tokens(data)

    def verify_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )

            exp = datetime.utcfromtimestamp(payload["exp"])

            if exp < datetime.utcnow():
                raise UnAuthorized("Token is expired")

        except JWTError:
            raise UnAuthorized()
        return TokenPayload(**payload)
