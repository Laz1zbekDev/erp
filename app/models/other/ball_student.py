# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy import String, Integer, Enum, ForeignKey, SmallInteger

# from ...db.base import Base, TimeMixin


# class BallStudent(Base, TimeMixin):
#     __tablename__ = "ball_students"

#     ball_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     student_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False
#     )
#     teacher_id: Mapped[int] = mapped_column(
#         SmallInteger,
#         ForeignKey("teachers.teacher_id"),
#         nullable=False,
#     )
#     group_id: Mapped[int] = mapped_column(
#         SmallInteger, ForeignKey("groups.group_id"), nullable=False
#     )
#     science_id: Mapped[int] = mapped_column(
#         SmallInteger,
#         ForeignKey("sciences.science_id"),
#         nullable=False,
#     )
#     last_week_ball: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
#     last_month_ball: Mapped[int] = mapped_column(
#         SmallInteger, nullable=False, default=0
#     )
#     last_3_month_ball: Mapped[int] = mapped_column(
#         SmallInteger, nullable=False, default=0
#     )
#     total_ball: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)


# class BallTransaction(Base, Time):
#     __tablename__ = "ball_transactions"

#     transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     ball_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("ball_students.ball_id", ondelete="CASCADE"), nullable=False
#     )
#     teacher_id: Mapped[int] = mapped_column(
#         SmallInteger,
#         ForeignKey("teachers.teacher_id"),
#         nullable=False,
#     )
#     group_id: Mapped[int] = mapped_column(
#         SmallInteger, ForeignKey("groups.group_id"), nullable=False
#     )
#     lesson_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("lessons.lesson_id"), nullable=False
#     )
#     ball_amount: Mapped[int] = mapped_column(SmallInteger, nullable=False)
