from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.expense import Expense


class Group(Base, TimestampMixin):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Relationships
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="groups_created",
        foreign_keys=[creator_id],
    )
    members: Mapped[List["GroupMember"]] = relationship(
        "GroupMember",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense",
        back_populates="group",
    )

    def __repr__(self) -> str:
        return f"<Group id={self.id} name='{self.name}'>"


class GroupMember(Base):
    __tablename__ = "group_members"
    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), default="member", nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    group: Mapped["Group"] = relationship("Group", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="group_memberships")

    def __repr__(self) -> str:
        return f"<GroupMember group_id={self.group_id} user_id={self.user_id}>"
