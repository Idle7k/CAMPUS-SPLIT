from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group
    from app.models.vendor import Vendor
    from app.models.payment import Payment, PaymentAllocation


class Expense(Base, TimestampMixin):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    vendor_id: Mapped[int] = mapped_column(
        ForeignKey("vendors.id", ondelete="RESTRICT"),
        nullable=False,
    )
    group_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("groups.id", ondelete="SET NULL"),
        nullable=True,
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Financial amount strictly in integer paise (₹1 = 100 paise)
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    
    split_type: Mapped[str] = mapped_column(
        String(20),
        default="equal",
        nullable=False,
    )  # equal, custom, percentage
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
    )  # active, settled, archived

    # Relationships
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="expenses_created",
        foreign_keys=[creator_id],
    )
    vendor: Mapped["Vendor"] = relationship(
        "Vendor",
        back_populates="expenses",
        foreign_keys=[vendor_id],
    )
    group: Mapped[Optional["Group"]] = relationship(
        "Group",
        back_populates="expenses",
        foreign_keys=[group_id],
    )
    shares: Mapped[List["ExpenseShare"]] = relationship(
        "ExpenseShare",
        back_populates="expense",
        cascade="all, delete-orphan",
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="expense",
        foreign_keys="Payment.expense_id",
    )

    def __repr__(self) -> str:
        return f"<Expense id={self.id} desc='{self.description}' total_paise={self.total_amount}>"


class ExpenseShare(Base, TimestampMixin):
    __tablename__ = "expense_shares"
    __table_args__ = (
        UniqueConstraint("expense_id", "user_id", name="uq_expense_user_share"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expenses.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    
    # Share amount strictly in integer paise
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    
    status: Mapped[str] = mapped_column(
        String(20),
        default="unpaid",
        nullable=False,
    )  # unpaid, partially_paid, paid

    # Relationships
    expense: Mapped["Expense"] = relationship(
        "Expense",
        back_populates="shares",
        foreign_keys=[expense_id],
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="expense_shares",
        foreign_keys=[user_id],
    )
    payment_allocations: Mapped[List["PaymentAllocation"]] = relationship(
        "PaymentAllocation",
        back_populates="expense_share",
        foreign_keys="PaymentAllocation.expense_share_id",
    )

    def __repr__(self) -> str:
        return f"<ExpenseShare expense_id={self.expense_id} user_id={self.user_id} amount_paise={self.amount}>"
