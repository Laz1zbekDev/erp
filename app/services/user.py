from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import User
from ..core import hash_password, verify_password
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


async def change_user_password(
    session: AsyncSession, user_id: int, password: str, new_password: str
) -> None:
    user = await verify_user_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User topilmadi")
    check = verify_password(password, user.hashed_password)
    if not check:
        raise HTTPException(status_code=400, detail="Parol xato")
    hashed_password = hash_password(new_password)
    user.hashed_password = hashed_password
    return user
