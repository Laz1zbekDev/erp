from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Enum, Boolean, Identity

from ..db.base import Base, TimeMixin
from ..utils.enums import UserRole


class User(Base, TimeMixin):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer, Identity(start=10000, increment=1), primary_key=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )

    status: Mapped[bool] = mapped_column(Boolean, default=True)

    teacher: Mapped["Teacher"] = relationship(
        "Teacher", back_populates="user", uselist=False
    )
    admin: Mapped["Admin"] = relationship("Admin", back_populates="user", uselist=False)
    superadmin: Mapped["SuperAdmin"] = relationship(
        "SuperAdmin", back_populates="user", uselist=False
    )
