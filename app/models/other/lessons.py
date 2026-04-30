# from decimal import Decimal
# from datetime import datetime, time

# from sqlalchemy.orm import Mapped, mapped_column
# from sqlalchemy import (
#     TIMESTAMP,
#     String,
#     Integer,
#     Enum,
#     Numeric,
#     SmallInteger,
#     ForeignKey,
#     TIME,
# )

# from ...db.base import Base, TimeMixin
# from ...utils.enums import GroupStatus


# class Lesson(Base):
#     __tablename__ = "lessons"

#     lesson_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     group_id: Mapped[int] = mapped_column(
#         SmallInteger, ForeignKey("groups.group_id"), nullable=False
#     )
#     teacher_id: Mapped[int] = mapped_column(
#         SmallInteger,
#         ForeignKey("teachers.teacher_id"),
#         nullable=False,
#     )
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
