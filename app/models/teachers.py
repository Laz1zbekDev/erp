from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, SmallInteger, ForeignKey, Numeric, Boolean

from ..db.base import Base, TimeMixin


class Teacher(Base, TimeMixin):
    __tablename__ = "teachers"

    teacher_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        unique=True,
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    salary: Mapped[Decimal] = mapped_column(Numeric(11, 2), nullable=False, default=0)
    status: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="teacher")
