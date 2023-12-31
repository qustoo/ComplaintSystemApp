from fastapi import APIRouter

from managers import UserManager
from schemas.request import UserLoginIn, UserRegisterIn

router = APIRouter(tags=["Auth"])


@router.post("/register/", status_code=201)
async def register(user_data: UserRegisterIn):
    token = await UserManager.register(user_data)
    return {"Token": token}


@router.post("/login/", status_code=201)
async def login(user_data: UserLoginIn):
    token = await UserManager.login(user_data)
    return {"token": token}
