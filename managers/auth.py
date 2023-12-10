from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy import select
from models import User, RoleType
from config import settings
from datetime import datetime, timedelta


class AuthManager:
    @staticmethod
    def encode_token(user):
        try:
            payload = {
                "sub": user.id,
                "exp": datetime.utcnow() + timedelta(minutes=120),
            }
            token = jwt.encode(payload, settings.JWT_SECRET, settings.ALGORITHM)
            return token
        except Exception as err:
            print(err)
            ...
            # log this exception


class CustomHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        _res = await super().__call__(request)
        try:
            payload = jwt.decode(
                _res.credentials, settings.JWT_SECRET, settings.ALGORITHM
            )
            user = select(User).filter(User.c.id == payload.get("sub"))
            # state - should include the value of the anti-forgery unique session token,
            request.state.user = user
            return payload
        except JWTError as err:
            print(f"{err=}")
            raise HTTPException(status_code=401, detail="failed to decode jwt")


def is_complainer(request: Request):
    if request.state.user.file is not RoleType.complainer:
        raise HTTPException(403, "Forbidden")


def is_approver(request: Request):
    if request.state.user.file is not RoleType.approver:
        raise HTTPException(403, "Forbidden")


def is_admin(request: Request):
    if request.state.user.file is not RoleType.admin:
        raise HTTPException(403, "Forbidden")
