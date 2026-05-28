from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
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
        first_name=data.first_name.strip().capitalize(),
        last_name=data.last_name.strip().capitalize(),
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
        first_name=first_name.strip().capitalize(),
        last_name=last_name.strip().capitalize(),
    )
    session.add(superadmin)
    await session.flush()
    return superadmin


async def get_all_superadmins(session):
    result = await session.execute(select(SuperAdmin))
    superadmins = result.scalars().first()
    return superadmins


async def get_all_admins(session: AsyncSession, status: bool) -> list[Admin]:
    if status:
        result = await session.execute(
            select(Admin).where(Admin.status).order_by(Admin.created_at.desc())
        )
    else:
        result = await session.execute(
            select(Admin).order_by(Admin.created_at.desc())
        )
    admins = result.scalars().all()
    return admins


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


async def get_all_admins_and_transactions(session: AsyncSession):
    result = await session.execute(
        select(Admin)
        .where(Admin.status)
        .options(
            selectinload(Admin.student_transactions),
            selectinload(Admin.teacher_transactions),
        )
    )
    admins = result.scalars().all()
    return admins


async def delete_admin(session: AsyncSession, admin_id: int) -> None:
    result = await session.execute(
        select(Admin)
        .where(Admin.admin_id == admin_id, Admin.status)
        .options(selectinload(Admin.user))
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=404, detail="admin topilmadi")
    user = admin.user
    user.status = False
    admin.status = False
