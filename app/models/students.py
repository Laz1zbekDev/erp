from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Boolean, TIMESTAMP, and_


from ..db.base import Base, TimeMixin


class Student(Base, TimeMixin):
    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=True)

    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary="student_groups",
        primaryjoin="and_(Student.student_id == student_groups.c.student_id, student_groups.c.status == True)",
        secondaryjoin="Group.group_id == student_groups.c.group_id",
        back_populates="students",
    )
    contact: Mapped["StudentContact"] = relationship(
        "StudentContact", back_populates="student"
    )
    student_discount: Mapped[list["StudentDiscount"]] = relationship(
        "StudentDiscount", back_populates="student"
    )
    student_per_dates: Mapped[list["StudentPermissionDate"]] = relationship(
        "StudentPermissionDate", back_populates="student"
    )
    student_transactions: Mapped[list["StudentTransaction"]] = relationship(
        "StudentTransaction", back_populates="student"
    )
