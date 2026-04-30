# from decimal import Decimal
# from datetime import time

# from sqlalchemy.orm import Mapped, mapped_column
# from sqlalchemy import (
#     String,
#     Integer,
#     Enum,
#     Numeric,
#     SmallInteger,
#     ForeignKey,
#     TIME,
#     func,
# )

# from ...db.base import Base, TimeMixin


# class Attendance(Base):
#     __tablename__ = "attendances"

#     attendance_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     student_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False
#     )
#     group_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("groups.group_id"), nullable=False
#     )
#     lesson_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("lessons.lesson_id"), nullable=False
#     )
#     attendance_date: Mapped[time] = mapped_column(
#         TIME, nullable=False, server_default=func.now()
#     )
