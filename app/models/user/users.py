from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Enum

from ...db.base import Base, Time
from ...utils.enums import UserRole


class User(Base, Time):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum"), nullable=False
    )
