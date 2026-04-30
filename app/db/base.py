from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import TIMESTAMP, func


class Base(DeclarativeBase):
    pass


class TimeMixin:
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(), server_default=func.now(), onupdate=func.now()
    )
