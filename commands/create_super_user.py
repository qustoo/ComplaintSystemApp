import os
import sys

# Харкод импорт из другой папки
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)
from sqlalchemy import insert
from models import User, RoleType
from database import async_session_factory
import asyncclick as click


@click.command()
@click.option("-f", "--first_name", type=str, required=True)
@click.option("-l", "--last_name", type=str, required=True)
@click.option("-e", "--email", type=str, required=True)
@click.option("-p", "--phone", type=str, required=True)
@click.option("-i", "--iban", type=str, required=True)
@click.option("-pa", "--password", type=str, required=True)
async def create_user(first_name, last_name, email, phone, iban, password):
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "iban": iban,
        "password": password,
        "role": RoleType.admin,
    }
    async with async_session_factory() as session:
        stmt = insert(User).values(user_data)
        await session.execute(stmt)
        await session.commit()


if __name__ == "__main__":
    create_user(_anyio_backend="asyncio")
