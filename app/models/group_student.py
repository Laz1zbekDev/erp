from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    Enum,
    ForeignKey,
    SmallInteger,
    Time,
    TIMESTAMP,
    Boolean,
)

from ..db.base import Base, TimeMixin


class StudentGr(Base, TimeMixin):
    __tablename__ = "student_groups"

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.student_id"),
        primary_key=True,
        index=True,
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.group_id"), primary_key=True, index=True
    )

    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
