from passlib.context import CryptContext
from sqlalchemy import insert
from managers import AuthManager
from models import User
from database import async_session_factory
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


class UserManager:
    async def register(self, user_data):
        async with async_session_factory() as session:
            user_data.password = get_password_hash(user_data.password)
            stmt = insert(User).values(**user_data.model_dump()).returning(User)
            _created_user = await session.execute(stmt)
            _created_user_fullname = _created_user.scalars().one().id
            return AuthManager.encode_token(user_data)
            # token = create_access_token(data={"sub": _created_user_fullname})
            # return {"token": token}