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


class Group(Base, TimeMixin):
    __tablename__ = "groups"

    group_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    teacher_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("teachers.teacher_id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    science_name: Mapped[int] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    teacher_percent: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    class_day: Mapped[str] = mapped_column(String(100), nullable=False)
    class_date: Mapped[time] = mapped_column(TIME, nullable=False)
    status: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="groups")
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
    student_transactions: Mapped[list["StudentTransaction"]] = relationship(
        "StudentTransaction", back_populates="group"
    )
    student_discounts: Mapped[list["StudentDiscount"]] = relationship(
        "StudentDiscount", back_populates="group"
    )
