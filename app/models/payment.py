from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.vendor import Vendor
    from app.models.expense import Expense, ExpenseShare
    from app.models.ledger import LedgerEntry


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    vendor_id: Mapped[int] = mapped_column(
        ForeignKey("vendors.id", ondelete="RESTRICT"),
        nullable=False,
    )
    expense_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("expenses.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Payment amount strictly in integer paise
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    
    method: Mapped[str] = mapped_column(String(20), default="upi", nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )  # pending, reported_paid, confirmed_demo, failed, cancelled
    
    reference_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=True,
    )
    confirmation_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    payer: Mapped["User"] = relationship(
        "User",
        back_populates="payments_made",
        foreign_keys=[payer_id],
    )
    vendor: Mapped["Vendor"] = relationship(
        "Vendor",
        back_populates="payments",
        foreign_keys=[vendor_id],
    )
    expense: Mapped[Optional["Expense"]] = relationship(
        "Expense",
        back_populates="payments",
        foreign_keys=[expense_id],
    )
    allocations: Mapped[List["PaymentAllocation"]] = relationship(
        "PaymentAllocation",
        back_populates="payment",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Payment id={self.id} amount_paise={self.amount} status='{self.status}'>"


class PaymentAllocation(Base):
    __tablename__ = "payment_allocations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
    )
    expense_share_id: Mapped[int] = mapped_column(
        ForeignKey("expense_shares.id", ondelete="RESTRICT"),
        nullable=False,
    )
    
    # Allocated amount in integer paise
    allocated_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    payment: Mapped["Payment"] = relationship(
        "Payment",
        back_populates="allocations",
        foreign_keys=[payment_id],
    )
    expense_share: Mapped["ExpenseShare"] = relationship(
        "ExpenseShare",
        back_populates="payment_allocations",
        foreign_keys=[expense_share_id],
    )
    ledger_entries: Mapped[List["LedgerEntry"]] = relationship(
        "LedgerEntry",
        back_populates="payment_allocation",
    )

    def __repr__(self) -> str:
        return f"<PaymentAllocation id={self.id} payment_id={self.payment_id} share_id={self.expense_share_id} amount_paise={self.allocated_amount}>"
