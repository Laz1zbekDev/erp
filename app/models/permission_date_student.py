from datetime import datetime, date

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Date,
    String,
    Integer,
    Enum,
    ForeignKey,
    SmallInteger,
    TIMESTAMP,
    func,
    Boolean,
)

from ..db.base import Base, TimeMixin


class StudentPermissionDate(Base, TimeMixin):
    __tablename__ = "student_permission_dates"

    permission_date_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.student_id"),
        nullable=False,
        index=True,
    )
    group_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("groups.group_id"), nullable=False
    )
    permission_date: Mapped[date] = mapped_column(
        Date(), nullable=False, server_default=func.now()
    )
    pending_deadline: Mapped[date] = mapped_column(
        Date(), nullable=False, server_default=func.now()
    )

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="student_per_dates",
    )
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="student_per_dates",
    )
