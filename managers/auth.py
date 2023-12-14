from datetime import datetime, timedelta

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy import select

from config import settings
from database import async_session_factory
from models import RoleType, User


class AuthManager:
    @staticmethod
    def encode_token(user):
        try:
            payload = {
                "sub": str(user.id),  # subject must be a string!!!!!! Это по поводу sub
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
        payload = jwt.decode(
            _res.credentials, key=settings.JWT_SECRET, algorithms=[settings.ALGORITHM]
        )
        async with async_session_factory() as session:
            stmt = select(User).filter(User.id == int(payload.get("sub")))
            _user = await session.execute(stmt)
            _user = _user.scalars().one_or_none()
        # state - should include the value of the anti-forgery unique session token,
        request.state.user = _user
        return payload

        # except JWTError as err:
        #     print(f"{err=}")
        #     raise HTTPException(status_code=401, detail="failed to decode jwt")


oauth2_schema = CustomHTTPBearer()


def is_complainer(request: Request):
    if request.state.user.role is not RoleType.complainer:
        raise HTTPException(403, "Forbidden")


def is_approver(request: Request):
    if request.state.user.role is not RoleType.approver:
        raise HTTPException(403, "Forbidden")


def is_admin(request: Request):
    if request.state.user.role is not RoleType.admin:
        raise HTTPException(403, "Forbidden")
