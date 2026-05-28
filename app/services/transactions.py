from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest import result

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..utils.enums import DiscountType
from ..models import AdminTransaction, StudentTransaction, TeacherTransaction
from .teacher import get_teacher_by_id


async def get_student_transactions(
    session: AsyncSession,
    start: datetime,
    end: datetime,
    limit: int,
    offset: int,
    student_id: int | None = None,
    teacher_id: int | None = None,
    group_id: int | None = None,
    admin_id: int | None = None,
) -> list[StudentTransaction | None]:
    stmt = select(StudentTransaction).where(
        StudentTransaction.created_at >= start,
        StudentTransaction.created_at < end,
    )
    if student_id is not None:
        stmt = stmt.where(StudentTransaction.student_id == student_id)
    if teacher_id is not None:
        stmt = stmt.where(StudentTransaction.teacher_id == teacher_id)
    if group_id is not None:
        stmt = stmt.where(StudentTransaction.group_id == group_id)
    if admin_id is not None:
        stmt = stmt.where(StudentTransaction.admin_id == admin_id)
    stmt = (
        stmt.options(
            selectinload(StudentTransaction.student),
            selectinload(StudentTransaction.teacher),
            selectinload(StudentTransaction.group),
            selectinload(StudentTransaction.admin),
        )
        .limit(limit)
        .offset(offset)
        .order_by(StudentTransaction.created_at.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def sum_student_transactions(
    session: AsyncSession,
    start: datetime,
    end: datetime,
    student_id: int | None = None,
    teacher_id: int | None = None,
    group_id: int | None = None,
    admin_id: int | None = None,
) -> Decimal:
    stmt = select(func.sum(StudentTransaction.amount)).where(
        StudentTransaction.created_at >= start,
        StudentTransaction.created_at < end,
    )
    if student_id is not None:
        stmt = stmt.where(StudentTransaction.student_id == student_id)
    if teacher_id is not None:
        stmt = stmt.where(StudentTransaction.teacher_id == teacher_id)
    if group_id is not None:
        stmt = stmt.where(StudentTransaction.group_id == group_id)
    if admin_id is not None:
        stmt = stmt.where(StudentTransaction.admin_id == admin_id)
    result = await session.execute(stmt)
    return result.scalar() or Decimal(0)


async def create_student_transactions(
    session: AsyncSession,
    admin_id: int,
    student_id: int,
    group_id: int,
    teacher_id: int,
    from_when: date,
    until_when: date,
    student_discount: int,
    discount_type: DiscountType,
    center_share: Decimal,
    teacher_share: Decimal,
    amount: int,
) -> StudentTransaction:
    transaction = StudentTransaction(
        admin_id=admin_id,
        student_id=student_id,
        group_id=group_id,
        teacher_id=teacher_id,
        from_when=from_when,
        until_when=until_when,
        student_discount=student_discount,
        discount_type=discount_type,
        center_share=center_share,
        teacher_share=teacher_share,
        amount=amount,
    )
    session.add(transaction)
    await session.flush()

    return transaction


async def get_teacher_sum(
    session: AsyncSession,
    start: datetime,
    end: datetime,
    student_id: int | None = None,
    teacher_id: int | None = None,
    group_id: int | None = None,
    admin_id: int | None = None,
) -> Decimal:
    stmt = select(func.sum(StudentTransaction.teacher_share)).where(
        StudentTransaction.created_at >= start,
        StudentTransaction.created_at < end,
    )
    if student_id is not None:
        stmt = stmt.where(StudentTransaction.student_id == student_id)
    if teacher_id is not None:
        stmt = stmt.where(StudentTransaction.teacher_id == teacher_id)
    if group_id is not None:
        stmt = stmt.where(StudentTransaction.group_id == group_id)
    if admin_id is not None:
        stmt = stmt.where(StudentTransaction.admin_id == admin_id)
    result = await session.execute(stmt)
    return result.scalar() or Decimal(0)


async def count_student_transactions(
    session: AsyncSession,
    start: datetime,
    end: datetime,
    student_id: int | None = None,
    teacher_id: int | None = None,
    group_id: int | None = None,
    admin_id: int | None = None,
) -> int:
    stmt = select(func.count(StudentTransaction.tr_id)).where(
        StudentTransaction.created_at >= start,
        StudentTransaction.created_at < end,
    )
    if student_id is not None:
        stmt = stmt.where(StudentTransaction.student_id == student_id)
    if teacher_id is not None:
        stmt = stmt.where(StudentTransaction.teacher_id == teacher_id)
    if group_id is not None:
        stmt = stmt.where(StudentTransaction.group_id == group_id)
    if admin_id is not None:
        stmt = stmt.where(StudentTransaction.admin_id == admin_id)
    result = await session.execute(stmt)
    return result.scalar()


async def get_teacher_transactions(
    session: AsyncSession,
    limit: int | None = 20,
    offset: int | None = 0,
    start: datetime | None = None,
    end: datetime | None = None,
    teacher_id: int | None = None,
    admin_id: int | None = None,
):
    if start is None or end is None:
        stmt = select(TeacherTransaction).where(
            TeacherTransaction.created_at
            < datetime(
                date.today().year, date.today().month, date.today().day, 23, 59, 59
            ),
        )
    else:
        stmt = select(TeacherTransaction).where(
            TeacherTransaction.created_at >= start,
            TeacherTransaction.created_at < end,
        )
    if teacher_id is not None:
        stmt = stmt.where(TeacherTransaction.teacher_id == teacher_id)
    if admin_id is not None:
        stmt = stmt.where(TeacherTransaction.admin_id == admin_id)
    stmt = (
        stmt.options(
            selectinload(TeacherTransaction.teacher),
            selectinload(TeacherTransaction.admin),
        )
        .limit(limit)
        .offset(offset)
        .order_by(TeacherTransaction.created_at.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_teacher_transactions(
    session: AsyncSession,
    start: datetime | None = None,
    end: datetime | None = None,
    teacher_id: int | None = None,
    admin_id: int | None = None,
) -> int:
    if start is None or end is None:
        stmt = select(func.count(TeacherTransaction.tr_id)).where(
            TeacherTransaction.created_at
            < datetime(
                date.today().year, date.today().month, date.today().day, 23, 59, 59
            ),
        )
    else:
        stmt = select(func.count(TeacherTransaction.tr_id)).where(
            TeacherTransaction.created_at >= start,
            TeacherTransaction.created_at < end,
        )
    if teacher_id:
        stmt = stmt.where(TeacherTransaction.teacher_id == teacher_id)
    if admin_id:
        stmt = stmt.where(TeacherTransaction.admin_id == admin_id)
    result = await session.execute(stmt)
    return result.scalar() or 0


async def sum_teacher_transactions(
    session: AsyncSession,
    start: datetime,
    end: datetime,
    admin_id: int | None = None,
    teacher_id: int | None = None,
) -> int:
    stmt = select(func.sum(TeacherTransaction.amount)).where(
        TeacherTransaction.created_at >= start,
        TeacherTransaction.created_at < end,
    )
    if admin_id is not None:
        stmt = stmt.where(TeacherTransaction.admin_id == admin_id)
    if teacher_id is not None:
        stmt = stmt.where(TeacherTransaction.teacher_id == teacher_id)
    result = await session.execute(stmt)
    return result.scalar() or 0


async def create_teacher_transaction(
    session: AsyncSession,
    admin_id: int,
    teacher_id: int,
    amount: Decimal,
    description: str | None = None,
) -> TeacherTransaction:
    transaction = TeacherTransaction(
        admin_id=admin_id,
        teacher_id=teacher_id,
        amount=amount,
        description=description,
    )
    teacher = await get_teacher_by_id(session, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")
    teacher.salary -= Decimal(str(amount))
    session.add(transaction)
    return transaction


async def get_admin_transactions(
    session: AsyncSession,
    start: datetime,
    end: datetime,
    limit: int,
    offset: int,
    admin_id: int | None = None,
) -> list[AdminTransaction | None]:
    stmt = select(AdminTransaction).where(
        AdminTransaction.created_at >= start,
        AdminTransaction.created_at < end,
    )
    if admin_id is not None:
        stmt = stmt.where(AdminTransaction.admin_id == admin_id)
    stmt = stmt.limit(limit).offset(offset).order_by(AdminTransaction.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_admin_transactions(
    session: AsyncSession,
    start: datetime,
    end: datetime,
    admin_id: int | None = None,
) -> int:
    stmt = select(func.count(AdminTransaction.tr_id)).where(
        AdminTransaction.created_at >= start,
        AdminTransaction.created_at < end,
    )
    if admin_id is not None:
        stmt = stmt.where(AdminTransaction.admin_id == admin_id)
    result = await session.execute(stmt)
    return result.scalar()


async def get_superadmin_transactions(
    session: AsyncSession,
    start: datetime,
    end: datetime,
    limit: int,
    offset: int,
    admin_id: int | None = None,
) -> list[AdminTransaction | None]:
    if not start:
        start = datetime(
            date.today().year, date.today().month, date.today().day, 0, 0, 0
        )
    if not end:
        end = datetime(
            date.today().year, date.today().month, date.today().day, 23, 59, 59
        )
    stmt = select(AdminTransaction).where(
        AdminTransaction.created_at >= start,
        AdminTransaction.created_at < end,
    )
    if admin_id is not None:
        stmt = stmt.where(AdminTransaction.admin_id == admin_id)
    stmt = stmt.options(selectinload(AdminTransaction.admin))
    stmt = stmt.limit(limit).offset(offset).order_by(AdminTransaction.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_superadmin_transactions(
    session: AsyncSession,
    start: datetime,
    end: datetime,
    admin_id: int | None = None,
) -> int:
    if not start:
        start = datetime(
            date.today().year, date.today().month, date.today().day, 0, 0, 0
        )
    if not end:
        end = datetime(
            date.today().year, date.today().month, date.today().day, 23, 59, 59
        )
    stmt = select(func.count(AdminTransaction.tr_id)).where(
        AdminTransaction.created_at >= start,
        AdminTransaction.created_at < end,
    )
    if admin_id is not None:
        stmt = stmt.where(AdminTransaction.admin_id == admin_id)
    result = await session.execute(stmt)
    return result.scalar()


async def sum_admin_transactions(
    session: AsyncSession,
    start: datetime,
    end: datetime,
    admin_id: int | None = None,
) -> int:
    stmt = select(func.sum(AdminTransaction.amount)).where(
        AdminTransaction.created_at >= start,
        AdminTransaction.created_at < end,
    )
    if admin_id is not None:
        stmt = stmt.where(AdminTransaction.admin_id == admin_id)
    result = await session.execute(stmt)
    return result.scalar() or 0


async def create_admin_transaction(
    session: AsyncSession,
    admin_id: int,
    amount: int,
    description: str | None = None,
) -> AdminTransaction:
    transaction = AdminTransaction(
        admin_id=admin_id,
        amount=amount,
        description=description,
    )
    session.add(transaction)

    return transaction
