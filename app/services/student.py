from datetime import datetime, date, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, update
from sqlalchemy.orm import selectinload

from .user import create_user
from .group import get_group_by_id
from ..models import (
    Student,
    StudentContact,
    StudentPermissionDate,
    StudentDiscount,
    StudentGr,
)
from ..schemas import RegisterStudent
from ..utils.enums import DiscountType, UserRole


async def create_student(session: AsyncSession, data: RegisterStudent) -> Student:

    student = Student(
        first_name=data.first_name,
        last_name=data.last_name,
    )
    session.add(student)
    await session.flush()
    return student


async def add_student_group(session: AsyncSession, student_id: int, group_id: int):
    pass


async def create_student_contact(
    session: AsyncSession, student_id: int, data: RegisterStudent
):
    contact = StudentContact(
        student_id=student_id,
        student_number=data.student_number,
        student_parent_number=data.student_parent_number,
        student_telegram=data.student_telegram,
        student_parent_telegram=data.student_parent_telegram,
    )

    session.add(contact)
    await session.flush()
    return contact


async def create_student_permission(
    session: AsyncSession,
    student_id: int,
    group_id: int,
    permission_date: datetime | None = datetime.now().date(),
    pending_dedline: datetime | None = datetime.now().date(),
) -> StudentPermissionDate:
    per = StudentPermissionDate(
        student_id=student_id,
        group_id=group_id,
        permission_date=permission_date,
        pending_deadline=pending_dedline,
    )

    session.add(per)
    await session.flush()

    return per


async def create_student_discount(
    session: AsyncSession,
    student_id: int,
    teacher_id: int,
    group_id: int,
    discount_amount: int = 0,
    discount_type: DiscountType = DiscountType.BOTH,
) -> StudentDiscount:
    discount = StudentDiscount(
        student_id=student_id,
        teacher_id=teacher_id,
        group_id=group_id,
        discount_amount=discount_amount,
        discount_type=discount_type,
    )

    session.add(discount)
    await session.flush()
    return discount


async def all_student_number(session: AsyncSession) -> int:
    result = await session.execute(
        select(func.count(Student.student_id)).where(Student.status)
    )
    return result.scalar_one()


async def get_student_by_id(session: AsyncSession, student_id: int) -> Student | None:
    student = await session.execute(
        select(Student).where(Student.student_id == student_id, Student.status)
    )

    return student.scalar_one_or_none()


async def get_student_full_info(session: AsyncSession, student_id: int) -> Student:
    stmt = (
        select(Student)
        .where(Student.student_id == student_id)
        .options(
            selectinload(Student.groups),
            selectinload(Student.contact),
            selectinload(Student.student_discount),
            selectinload(Student.student_per_dates),
        )
    )

    student = await session.execute(stmt)

    return student.scalar_one()


async def get_student_and_discount(session: AsyncSession, student_id: int):
    result = await session.execute(
        select(Student)
        .where(Student.student_id == student_id)
        .options(selectinload(Student.student_discount))
    )

    return result.scalar_one_or_none()


async def get_groups_by_student(session: AsyncSession, student_id: int):
    result = await session.execute(
        select(Student)
        .where(Student.student_id == student_id)
        .options(selectinload(Student.groups))
    )
    student = result.scalar_one_or_none()

    if student is None:
        raise HTTPException(status_code=404, detail="student topilmadi")

    return student


async def get_student_permission(
    session: AsyncSession, student_id, group_id: int
) -> StudentPermissionDate:
    result = await session.execute(
        select(StudentPermissionDate).where(
            StudentPermissionDate.student_id == student_id,
            StudentPermissionDate.group_id == group_id,
        )
    )

    return result.scalar_one_or_none()


async def get_student_per_and_student(
    session: AsyncSession, offset: int = 0, limit: int = 20
) -> list[StudentPermissionDate]:
    today = date.today()
    stmt = (
        select(StudentPermissionDate)
        .where(
            StudentPermissionDate.permission_date < today,
            StudentPermissionDate.pending_deadline < today,
        )
        .order_by(StudentPermissionDate.permission_date.asc())
        .options(
            selectinload(StudentPermissionDate.student).selectinload(Student.contact),
            selectinload(StudentPermissionDate.group),
        )
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def count_student_per_and_student(session: AsyncSession) -> int:
    today = date.today()

    stmt = (
        select(func.count())
        .select_from(StudentPermissionDate)
        .where(
            StudentPermissionDate.permission_date < today,
            StudentPermissionDate.pending_deadline < today,
        )
    )

    result = await session.execute(stmt)
    return result.scalar_one()


async def update_student_pending(session: AsyncSession, student_id: int, days: int):
    result = await session.execute(
        select(StudentPermissionDate).where(
            StudentPermissionDate.student_id == student_id
        )
    )
    check = result.scalar_one_or_none()
    if not check:
        raise HTTPException(status_code=404, detail="student topilmadi")

    check.pending_deadline = date.today() + timedelta(days=days)

    await session.commit()

    return check


async def update_student_name(
    session: AsyncSession,
    student_id: int,
    first_name: str | None,
    last_name: str | None,
) -> Student:
    result = await session.execute(
        select(Student).where(Student.student_id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="student topilmadi")

    student.first_name = first_name if first_name else student.first_name
    student.last_name = last_name if last_name else student.last_name

    await session.commit()
    await session.refresh(student)

    return student


async def update_student_contact(
    session: AsyncSession,
    student_id: int,
    student_num: str,
    student_parent_num: str,
    student_telegram: str,
    student_parent_telegram: str,
) -> StudentContact:
    result = await session.execute(
        select(StudentContact).where(StudentContact.student_id == student_id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException("bunday student id ga ega kontakt mavjud emas")

    contact.student_number = student_num if student_num else contact.student_number
    contact.student_parent_number = (
        student_parent_num if student_parent_num else contact.student_parent_number
    )

    contact.student_telegram = (
        student_telegram if student_telegram else contact.student_telegram
    )
    contact.student_parent_telegram = (
        student_parent_telegram
        if student_parent_telegram
        else contact.student_parent_telegram
    )

    await session.commit()
    await session.refresh(contact)

    return contact


async def update_student_permission(
    session: AsyncSession, student_id, group_id: int, permission_date: date
) -> StudentPermissionDate:
    result = await session.execute(
        select(StudentPermissionDate).where(
            StudentPermissionDate.student_id == student_id,
            StudentPermissionDate.group_id == group_id,
        )
    )

    per = result.scalar_one_or_none()
    if not per:
        raise HTTPException(status_code=404, detail="student uchun vaqt topilmadi")

    per.permission_date = permission_date
    per.pending_deadline = permission_date

    return per


async def upsert_student_discount(
    session: AsyncSession,
    student_id: int,
    group_id: int,
    discount: int,
    discount_type: DiscountType,
):
    result = await session.execute(
        select(StudentDiscount).where(
            StudentDiscount.student_id == student_id,
            StudentDiscount.group_id == group_id,
        )
    )
    check = result.scalar_one_or_none()
    if check:
        check.discount_amount = discount
        check.discount_type = discount_type
        return check

    student = await get_student_by_id(session, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student topilmadi")
    group = await get_group_by_id(session, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="guruh topilmadi")
    creating_discount = StudentDiscount(
        student_id=student_id,
        teacher_id=group.teacher_id,
        group_id=group_id,
        discount_amount=discount,
        discount_type=discount_type,
    )
    session.add(creating_discount)

    await session.flush()
    return creating_discount


async def delete_student(
    session: AsyncSession,
    student_id: int,
) -> None:
    student = await get_groups_by_student(session, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student topilmadi")
    student.status = False
    groups = student.groups
    for group in groups:
        await session.execute(
            delete(StudentPermissionDate).where(
                StudentPermissionDate.student_id == student_id,
                StudentPermissionDate.group_id == group.group_id,
            )
        )
        await session.execute(
            update(StudentGr)
            .where(
                StudentGr.student_id == student_id, StudentGr.group_id == group.group_id
            )
            .values(status=False)
        )
