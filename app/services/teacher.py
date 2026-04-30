from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from .user import create_user
from ..models import Teacher
from ..schemas import RegisterTeacher
from ..utils.enums import UserRole


async def create_teacher(session: AsyncSession, data: RegisterTeacher) -> Teacher:
    user_id = await create_user(session, data.password, UserRole.TEACHER)

    teacher = Teacher(
        user_id=user_id,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    session.add(teacher)
    await session.flush()
    return teacher


async def all_teacher_number(session: AsyncSession) -> int:
    result = await session.execute(
        select(func.count(Teacher.teacher_id)).where(Teacher.status)
    )
    return result.scalar()


async def get_teacher_by_id(session: AsyncSession, teacher_id: int) -> Teacher | None:
    result = await session.execute(
        select(Teacher).where(Teacher.teacher_id == teacher_id, Teacher.status)
    )

    return result.scalar_one_or_none()


async def update_teacher_salary(
    session: AsyncSession, teacher_id: int, price: int
) -> Teacher:
    teacher = await get_teacher_by_id(session, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")

    teacher.salary += Decimal(str(price))

    return teacher
