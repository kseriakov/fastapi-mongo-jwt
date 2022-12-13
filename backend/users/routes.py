from fastapi import APIRouter, Depends, status, HTTPException

from auth.schemas import TokensResponse
from .schema import UserCreate
from database.connection import Database
from auth.authentication import OAuth2UserAuthForm, auth_jwt
from .models import User


user_db = Database(User)

router = APIRouter(tags=["User"], prefix="/user")


@router.post("/singup", status_code=status.HTTP_201_CREATED)
async def sing_user_up(new_user: UserCreate) -> dict:
    email, password = new_user.email, new_user.password

    if await User.find_one(User.email == email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email already have another user",
        )

    user_create = User(
        email=email,
        password=auth_jwt.get_password_hash(password),
    )
    await user_db.create(user_create)
    return {"message": f"User with {email} created successful"}


@router.post("/singin", response_model=TokensResponse)
async def sing_user_in(payload: OAuth2UserAuthForm = Depends()):
    email, password = payload.email, payload.password

    user = await User.find_one(User.email == email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current user do not register on site",
        )

    tokens = auth_jwt.get_tokens(email, password, user.password)
    return TokensResponse(**tokens.dict(), token_type="bearer")
