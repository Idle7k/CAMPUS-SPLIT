from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.ledger import LedgerEntry


class Settlement(Base, TimestampMixin):
    """
    Represents full or partial repayment of a peer debt.
    Settlements reduce peer liabilities without modifying original expenses.
    """
    __tablename__ = "settlements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    ledger_entry_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ledger_entries.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Repayment amount strictly in integer paise
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    
    status: Mapped[str] = mapped_column(
        String(20),
        default="confirmed_demo",
        nullable=False,
    )  # reported, confirmed_demo, cancelled
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    payer: Mapped["User"] = relationship(
        "User",
        back_populates="settlements_paid",
        foreign_keys=[payer_id],
    )
    recipient: Mapped["User"] = relationship(
        "User",
        back_populates="settlements_received",
        foreign_keys=[recipient_id],
    )
    ledger_entry: Mapped[Optional["LedgerEntry"]] = relationship(
        "LedgerEntry",
        back_populates="settlements",
        foreign_keys=[ledger_entry_id],
    )

    def __repr__(self) -> str:
        return f"<Settlement id={self.id} payer={self.payer_id} -> recipient={self.recipient_id} amount_paise={self.amount}>"
