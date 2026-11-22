from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.expense import Expense
    from app.models.payment import PaymentAllocation
    from app.models.settlement import Settlement


class LedgerEntry(Base, TimestampMixin):
    """
    Peer liability record created strictly when one student's vendor payment
    covers another participant's expense share.
    """
    __tablename__ = "ledger_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    debtor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    creditor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    
    # Debt amount strictly in integer paise
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    
    expense_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("expenses.id", ondelete="SET NULL"),
        nullable=True,
    )
    payment_allocation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("payment_allocations.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="outstanding",
        nullable=False,
    )  # outstanding, partially_settled, settled
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    debtor: Mapped["User"] = relationship(
        "User",
        back_populates="debts_owed",
        foreign_keys=[debtor_id],
    )
    creditor: Mapped["User"] = relationship(
        "User",
        back_populates="credits_held",
        foreign_keys=[creditor_id],
    )
    expense: Mapped[Optional["Expense"]] = relationship(
        "Expense",
        foreign_keys=[expense_id],
    )
    payment_allocation: Mapped[Optional["PaymentAllocation"]] = relationship(
        "PaymentAllocation",
        back_populates="ledger_entries",
        foreign_keys=[payment_allocation_id],
    )
    settlements: Mapped[List["Settlement"]] = relationship(
        "Settlement",
        back_populates="ledger_entry",
    )

    def __repr__(self) -> str:
        return f"<LedgerEntry id={self.id} debtor={self.debtor_id} owes creditor={self.creditor_id} paise={self.amount}>"
