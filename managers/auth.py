from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy import select
from models import User
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
            request.state.user = user
            return payload
        except JWTError as err:
            print(f"{err=}")
            raise HTTPException(status_code=401, detail="failed to decode jwt")
