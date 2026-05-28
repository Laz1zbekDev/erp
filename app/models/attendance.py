from decimal import Decimal
from datetime import time

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    String,
    Integer,
    Enum,
    Numeric,
    SmallInteger,
    ForeignKey,
    TIME,
    func,
)

from ..db.base import Base, TimeMixin


class Attendance(Base, TimeMixin):
    __tablename__ = "attendances"

    attendance_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey("groups.group_id"), nullable=False)
    
