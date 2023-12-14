from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .enums import RoleType, State


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    role: Mapped[RoleType] = mapped_column(
        server_default=RoleType.complainer.name, nullable=False
    )
    iban: Mapped[str] = mapped_column(String(100))


class Complaint(Base):
    __tablename__ = "complaint"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    photo_url: Mapped[str] = mapped_column(String(256))
    amount: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[str] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    status: Mapped[State] = mapped_column(
        server_default=State.pending.name, nullable=False
    )
    complainer_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)


class Transaction(Base):
    __tablename__ = "transaction"
    id: Mapped[int] = mapped_column(primary_key=True)
    quote_id: Mapped[str] = mapped_column(String(120), nullable=False)
    transfer_id: Mapped[int] = mapped_column(nullable=False)
    target_account_id: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float]
    complaint_id: Mapped[int] = mapped_column(
        ForeignKey("complaint.id"), nullable=False
    )
