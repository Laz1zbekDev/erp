from decimal import Decimal
from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    SmallInteger,
    ForeignKey,
    Boolean,
    Text,
    Date,
    Enum,
    Numeric,
)

from ..db.base import Base, TimeMixin
from ..utils.enums import DiscountType


class AdminTransaction(Base, TimeMixin):
    __tablename__ = "admin_transaction"

    tr_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    admin_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("admins.admin_id"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    admin: Mapped["Admin"] = relationship("Admin", back_populates="admin_transactions")


class TeacherTransaction(Base, TimeMixin):
    __tablename__ = "teacher_transaction"

    tr_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    admin_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("admins.admin_id"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("teachers.teacher_id"), nullable=False
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    teacher: Mapped["Teacher"] = relationship(
        "Teacher", back_populates="teacher_transactions"
    )
    admin: Mapped["Admin"] = relationship(
        "Admin", back_populates="teacher_transactions"
    )


class StudentTransaction(Base, TimeMixin):
    __tablename__ = "student_transaction"

    tr_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    admin_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("admins.admin_id"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.student_id"), nullable=False
    )
    group_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("groups.group_id"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("teachers.teacher_id"), nullable=False
    )
    from_when: Mapped[date] = mapped_column(Date, nullable=False)
    until_when: Mapped[date] = mapped_column(Date, nullable=False)
    center_share: Mapped[Decimal] = mapped_column(Numeric(11, 2))
    teacher_share: Mapped[Decimal] = mapped_column(Numeric(11, 2))
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    student_discount: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    discount_type: Mapped[DiscountType] = mapped_column(
        Enum(
            DiscountType,
            name="discount_type_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=True,
    )

    student: Mapped["Student"] = relationship(
        "Student", back_populates="student_transactions"
    )
    teacher: Mapped["Teacher"] = relationship(
        "Teacher", back_populates="student_transactions"
    )
    group: Mapped["Group"] = relationship(
        "Group", back_populates="student_transactions"
    )
    admin: Mapped["Admin"] = relationship(
        "Admin", back_populates="student_transactions"
    )
