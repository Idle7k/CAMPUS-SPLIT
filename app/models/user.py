import enum
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.group import Group, GroupMember
    from app.models.expense import Expense, ExpenseShare
    from app.models.payment import Payment
    from app.models.ledger import LedgerEntry
    from app.models.settlement import Settlement


class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.STUDENT,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    groups_created: Mapped[List["Group"]] = relationship(
        "Group",
        back_populates="creator",
        foreign_keys="Group.creator_id",
    )
    group_memberships: Mapped[List["GroupMember"]] = relationship(
        "GroupMember",
        back_populates="user",
        foreign_keys="GroupMember.user_id",
    )
    expenses_created: Mapped[List["Expense"]] = relationship(
        "Expense",
        back_populates="creator",
        foreign_keys="Expense.creator_id",
    )
    expense_shares: Mapped[List["ExpenseShare"]] = relationship(
        "ExpenseShare",
        back_populates="user",
        foreign_keys="ExpenseShare.user_id",
    )
    payments_made: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="payer",
        foreign_keys="Payment.payer_id",
    )
    debts_owed: Mapped[List["LedgerEntry"]] = relationship(
        "LedgerEntry",
        back_populates="debtor",
        foreign_keys="LedgerEntry.debtor_id",
    )
    credits_held: Mapped[List["LedgerEntry"]] = relationship(
        "LedgerEntry",
        back_populates="creditor",
        foreign_keys="LedgerEntry.creditor_id",
    )
    settlements_paid: Mapped[List["Settlement"]] = relationship(
        "Settlement",
        back_populates="payer",
        foreign_keys="Settlement.payer_id",
    )
    settlements_received: Mapped[List["Settlement"]] = relationship(
        "Settlement",
        back_populates="recipient",
        foreign_keys="Settlement.recipient_id",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}' role='{self.role}'>"
