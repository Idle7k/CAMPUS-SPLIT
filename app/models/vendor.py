from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.expense import Expense
    from app.models.payment import Payment


class Vendor(Base, TimestampMixin):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    upi_id: Mapped[str] = mapped_column(String(100), nullable=False)
    qr_image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)

    # Relationships
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense",
        back_populates="vendor",
        foreign_keys="Expense.vendor_id",
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="vendor",
        foreign_keys="Payment.vendor_id",
    )

    def __repr__(self) -> str:
        return f"<Vendor id={self.id} name='{self.name}' upi_id='{self.upi_id}' is_active={self.is_active}>"
