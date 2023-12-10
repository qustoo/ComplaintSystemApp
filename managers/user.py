from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import insert, select
from managers import AuthManager
from models import User
from database import async_session_factory

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


class UserManager:
    @staticmethod
    async def register(user_data):
        async with async_session_factory() as session:
            user_data.password = get_password_hash(user_data.password)
            stmt = insert(User).values(**user_data.model_dump()).returning(User)
            _created_user = await session.execute(stmt)
            _created_user_obj = _created_user.scalars().one().id
            return AuthManager.encode_token(_created_user_obj)
            # token = create_access_token(data={"sub": _created_user_fullname})
            # return {"token": token}
    @staticmethod
    async def login(user_data):
        async with async_session_factory() as session:
            query = select(User).filter_by(User.email == user_data.email)
            result = await session.execute(query)
        _user = result.scalars().one_or_none()
        if not _user:
            raise HTTPException(400,'wrong email or pass')
        elif not verify_password(user_data.password,_user.password):
            raise HTTPException(400,'wrong email or pass')
