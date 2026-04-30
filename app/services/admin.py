from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


from .user import create_user
from ..models.admins import Admin, SuperAdmin
from ..schemas import RegisterAdmin
from ..utils.enums import UserRole


async def create_admin(session: AsyncSession, data: RegisterAdmin) -> Admin:
    user_id = await create_user(session, data.password, UserRole.ADMIN)
    admin = Admin(
        user_id=user_id,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    session.add(admin)
    await session.flush()
    return admin


async def create_superadmin(
    session: AsyncSession, password: str, first_name: str, last_name: str
) -> SuperAdmin:
    user_id = await create_user(session, password, UserRole.SUPERADMIN)

    superadmin = SuperAdmin(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
    )
    session.add(superadmin)
    await session.flush()
    return superadmin


async def get_all_superadmins(session):
    result = await session.execute(select(SuperAdmin))
    superadmins = result.scalars().first()
    return superadmins


async def get_superadmin_by_user_id(
    session: AsyncSession, user_id: int
) -> SuperAdmin | None:
    result = await session.execute(
        select(SuperAdmin).where(SuperAdmin.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_admin_by_user_id(session: AsyncSession, user_id: int) -> Admin | None:
    result = await session.execute(
        select(Admin).where(Admin.user_id == user_id, Admin.status)
    )
    return result.scalar_one_or_none()
