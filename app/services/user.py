from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import User
from ..core import hash_password
from ..utils.enums import UserRole


async def verify_user_id(session: AsyncSession, user_id: int) -> User | None:
    result = await session.execute(
        select(User).where(User.user_id == user_id, User.status)
    )
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, password: str, role: UserRole) -> int:
    hashed_password = hash_password(password)
    user = User(
        hashed_password=hashed_password,
        role=role,
    )
    session.add(user)
    await session.flush()
    return user.user_id
