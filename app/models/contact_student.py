from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Enum, ForeignKey

from ..db.base import Base, TimeMixin


class StudentContact(Base, TimeMixin):
    """bu sinfdan studentning contact malumotlari saqlanadi, student va parentning nomer va telegrami saqlanadi"""

    __tablename__ = "student_contacts"

    contact_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("students.student_id"),
        nullable=False,
        unique=True,
    )
    student_number: Mapped[str] = mapped_column(String(20), nullable=False)
    student_parent_number: Mapped[str] = mapped_column(String(20), nullable=False)
    student_telegram: Mapped[str] = mapped_column(String(30), nullable=True)
    student_parent_telegram: Mapped[str] = mapped_column(String(30), nullable=True)

    student: Mapped["Student"] = relationship("Student", back_populates="contact")
