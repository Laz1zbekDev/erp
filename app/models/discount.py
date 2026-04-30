from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import SmallInteger, String, Integer, Enum, ForeignKey, Numeric

from ..db.base import Base, TimeMixin
from ..utils.enums import DiscountType


class StudentDiscount(Base, TimeMixin):
    __tablename__ = "student_discounts"

    discount_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.student_id"),
        nullable=False,
        index=True,
    )
    teacher_id: Mapped[int] = mapped_column(
        SmallInteger,
        ForeignKey("teachers.teacher_id"),
        nullable=False,
        index=True,
    )
    group_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("groups.group_id"), nullable=False
    )
    discount_amount: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )
    discount_type: Mapped[DiscountType] = mapped_column(
        Enum(
            DiscountType,
            name="discount_type_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )

    student: Mapped["Student"] = relationship(
        "Student", back_populates="student_discount"
    )
