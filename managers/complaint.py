import uuid
from fastapi import Request
import os
from sqlalchemy import insert, select, update, delete
from utils.helpers import decode_photo
from constants import TEMP_FILE_ROLDER
from models import RoleType, State, Complaint
from database import async_session_factory
from services import S3Service

s3 = S3Service()


class ComplaintManager:
    @staticmethod
    async def get_complaints(user):
        async with async_session_factory() as session:
            query = select(Complaint)
            if user.role == RoleType.complainer:
                query = query.where(Complaint.complainer_id == user.id)
            elif user.role is not RoleType.approver:
                query = query.where(Complaint.status == State.pending)
            res = await session.execute(query)
            return res.scalars().all()

    @staticmethod
    async def create_complaint(complaint_data, user):
        complaint_data_dict = complaint_data.model_dump()
        encoded_photo = complaint_data_dict.pop("encoded_photo")
        extension = complaint_data_dict.pop("extension")
        name = f"{uuid.uuid4()}.{extension}"
        path = os.path.join(TEMP_FILE_ROLDER, name)
        decode_photo(path, encoded_photo)
        try:
            s3.upload(path, name, extension)
        except Exception as err:
            s3_status = err
        async with async_session_factory() as session:
            stmt = (
                insert(Complaint)
                .values(**complaint_data_dict, complainer_id=user.id)
                .returning(Complaint.id)
            )
            _id = (await session.execute(stmt)).scalar()
            await session.commit()
            _res = await session.execute(select(Complaint).where(Complaint.id == _id))
            return {"result": _res.scalars().one_or_none(), "s3_status": s3_status}

    @staticmethod
    async def delete_complaint(_id: int):
        stmt = delete(Complaint).filter_by(id=_id)
        async with async_session_factory() as session:
            await session.execute(stmt)
            await session.commit()

    @staticmethod
    async def approve(complaint_id: int):
        async with async_session_factory() as session:
            stmt = (
                update(Complaint)
                .values(status=State.approved)
                .filter_by(id=complaint_id)
            )
            await session.execute(stmt)
            await session.commit()

    @staticmethod
    async def reject(complaint_id: int):
        async with async_session_factory() as session:
            stmt = (
                update(Complaint)
                .values(status=State.rejected)
                .filter_by(id=complaint_id)
            )
            await session.execute(stmt)
            await session.commit()
