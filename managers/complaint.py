import os
import uuid

from sqlalchemy import delete, insert, select, update

from constants import TEMP_FILE_ROLDER
from database import async_session_factory
from models import Complaint, RoleType, State, Transaction
from services import S3Service, WiseService, ses, wise
from utils.helpers import decode_photo

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
            await ComplaintManager.issue_transaction(
                complaint_data["amount"],
                f"{complaint_data['first_name']} {complaint_data['last_name']}",
                complaint_data["iban"],
                _id,
            )
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
            transaction_stmt = select(Transaction).filter(Transaction,complaint_id = complaint_id)
            transaction_data = (await session.scalars(transaction_stmt)).one_or_none()
            try:
                wise.fund_transfer(transaction_data["transfer_id"])
                ses.send_mail(
                "Complaint approved!",
                "Congrats! Your claim is approved, check your bank account in 2 days for your refund")
            except Exception as err:
                return {"wise status": f'{err=}'}
                


    @staticmethod
    async def reject(complaint_id: int):
        async with async_session_factory() as session:
            stmt = (
                update(Complaint)
                .values(status=State.rejected)
                .filter_by(id=complaint_id).returning(Complaint.id)
            )
            _id = (await session.execute(stmt)).scalar()
            transaction_stmt = select(Transaction).filter_by(complaint_id = _id)
            transaction_data = (await session.scalars(transaction_stmt)).one_or_none()
            await session.commit()
            try:
                wise.cancel_funds(transaction_data["transfer_id"])
            except Exception as err:
                return {"wise status": f'{err=}'}      

    @staticmethod
    async def issue_transaction(amount, full_name, iban, complaint_id):
        wise_service = WiseService()
        quote_id = wise_service.create_quote(amount)
        recipient_id = wise_service.create_recipient_account(full_name, iban)
        transfer_id = wise_service.create_transfer(recipient_id, quote_id)
        data = {
            "quote_id": quote_id,
            "transfer_id": transfer_id,
            "target_account_id": str(recipient_id),
            "amount": amount,
            "complaint_id": complaint_id,
        }

        async with async_session_factory() as session:
            stmt = select(Transaction).update(data)
            await session.execute(stmt)
            await session.commit()
