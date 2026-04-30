from decimal import Decimal
from datetime import time

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    Enum,
    Numeric,
    SmallInteger,
    ForeignKey,
    TIME,
    Boolean,
)

from ..db.base import Base, TimeMixin
from ..utils.enums import GroupStatus


class Group(Base, TimeMixin):
    __tablename__ = "groups"

    group_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    teacher_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("teachers.teacher_id"), nullable=False, index=True
    )
    science_name: Mapped[int] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    teacher_percent: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    class_day: Mapped[str] = mapped_column(String(100), nullable=False)
    class_date: Mapped[time] = mapped_column(TIME, nullable=False)
    status: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    students: Mapped[list["Student"]] = relationship(
        "Student",
        secondary="student_groups",
        primaryjoin="Group.group_id == student_groups.c.group_id",
        secondaryjoin="and_(Student.student_id == student_groups.c.student_id, student_groups.c.status == True)",
        back_populates="groups",
    )
    student_per_dates: Mapped[list["StudentPermissionDate"]] = relationship(
        "StudentPermissionDate", back_populates="group"
    )
