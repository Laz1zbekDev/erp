from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, SmallInteger, ForeignKey, Boolean

from ..db.base import Base, TimeMixin


class Admin(Base, TimeMixin):
    __tablename__ = "admins"

    admin_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        unique=True,
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="admin")


class SuperAdmin(Base, TimeMixin):
    __tablename__ = "superadmins"

    superadmin_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        unique=True,
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="superadmin")
