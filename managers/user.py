from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import insert, select, update

from database import async_session_factory
from managers import AuthManager
from models import User
from models.enums import RoleType
from schemas.request import UserLoginIn, UserRegisterIn

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


class UserManager:
    @staticmethod
    async def register(user_data: UserRegisterIn):
        async with async_session_factory() as session:
            user_data.password = get_password_hash(user_data.password)
            stmt = insert(User).values(**user_data.model_dump()).returning(User)
            _returning_usr_obj = await session.execute(stmt)
            token = AuthManager.encode_token(_returning_usr_obj.scalars().one_or_none())
            await session.commit()
            return token

    @staticmethod
    async def login(user_data: UserLoginIn):
        async with async_session_factory() as session:
            query = select(User).filter(User.email == user_data.email)
            result = await session.execute(query)
        _user = result.scalars().one_or_none()
        if not _user:
            raise HTTPException(400, "user not found")
        elif not verify_password(user_data.password, _user.password):
            raise HTTPException(400, "wrong pass")
        return AuthManager.encode_token(_user)

    @staticmethod
    async def get_all_users():
        async with async_session_factory() as session:
            stmt = select(User)
            _res = await session.execute(stmt)
            return _res.scalars().all()

    @staticmethod
    async def get_user_by_email(_email):
        async with async_session_factory() as session:
            stmt = select(User).filter_by(email=_email)
            _res = await session.execute(stmt)
            return _res.scalars().all()

    @staticmethod
    async def change_role_status_by_user_id(new_role: RoleType, user_id: int):
        async with async_session_factory() as session:
            stmt = (
                update(User).filter_by(id=user_id).values(role=new_role).returning(User)
            )
            usr = (await session.execute(stmt)).one_or_none()
            if not usr:
                raise HTTPException(403, "user not found")
            await session.commit()
