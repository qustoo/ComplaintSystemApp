from fastapi import Request
from sqlalchemy import select, update
from models import RoleType, State, Complaint
from database import async_session_factory


class ComplaintManager:
    @staticmethod
    async def get_complaints(user):
        async with async_session_factory() as session:
            query = select(Complaint)
            if user.role is not RoleType.complainer:
                query = query.where(Complaint.complainer_id == user.id)
            elif user.role is not RoleType.approver:
                query = query.where(Complaint.status == State.pending)
            res = await session.execute(query)

    @staticmethod
    async def create_complaint(complaint_data):
        async with async_session_factory() as session:
            stmt = (
                update(Complaint)
                .values(**complaint_data.model_dump())
                .returning(Complaint.id)
            )
            _id = await session.execute(stmt)
            _res = await session.execute(select(Complaint).where(Complaint.id == _id))
            return _res.scalars().one_or_none()
