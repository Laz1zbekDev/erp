from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    ForeignKey,
    Numeric,
    TIMESTAMP,
    Enum,
    CheckConstraint,
)

from ..db.base import Base
from ..utils.enums import DiscountType


class Students(Base):
    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    permission_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    discount: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    discount_type: Mapped[str] = mapped_column(
        Enum(DiscountType, name="discount_type_enum")
    )
    status: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    ball: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (CheckConstraint("discount >= 0 AND discount <=100"),)
