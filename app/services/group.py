from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, update
from sqlalchemy.orm import selectinload

from ..models import Group, StudentGr, StudentPermissionDate, Student, StudentDiscount, Teacher
from ..schemas.group import CreateGroup, UpdateGroup, UpdateTeacherGroup


async def create_group(session: AsyncSession, data: CreateGroup) -> Group:
    group = Group(
        teacher_id=data.teacher_id,
        science_name=data.science_name,
        name=data.name,
        price=data.price,
        teacher_percent=data.teacher_percent,
        class_day=data.class_day,
        class_date=data.class_date,
    )

    session.add(group)
    await session.flush()

    return group


async def create_student_group(
    session: AsyncSession, student_id: int, group_id: int
) -> StudentGr:
    result = await session.execute(
        select(StudentGr).where(
            StudentGr.student_id == student_id,
            StudentGr.group_id == group_id,
            StudentGr.status,
        )
    )
    check = result.scalar_one_or_none()
    if check:
        raise HTTPException(
            status_code=409, detail="student allaqachon guruhga qo'shilgan"
        )

    studentgr = StudentGr(student_id=student_id, group_id=group_id)
    session.add(studentgr)
    await session.flush()

    return studentgr


async def all_group_number(session: AsyncSession) -> int:
    result = await session.execute(
        select(func.count(Group.group_id)).where(Group.status)
    )
    return result.scalar_one()


async def get_all_groups(session: AsyncSession) -> list[Group]:
    result = await session.scalars(select(Group).where(Group.status))

    return result.all()


async def student_is_group(
    session: AsyncSession, student_id: int, group_id: int
) -> StudentGr | None:
    result = await session.execute(
        select(StudentGr).where(
            StudentGr.student_id == student_id,
            StudentGr.group_id == group_id,
            StudentGr.status,
        )
    )

    return result.scalar_one_or_none()


async def get_students_by_group(session: AsyncSession, group_id: int):
    result = await session.execute(
        select(Group)
        .where(Group.group_id == group_id)
        .options(selectinload(Group.students), selectinload(Group.student_per_dates))
    )
    group = result.scalar_one_or_none()

    if group is None:
        return HTTPException(status_code=404, detail="guruh topilmadi")

    return group


async def get_groups(session: AsyncSession, limit: int, offset: int) -> list[Group]:

    result = await session.scalars(
        select(Group).where(Group.status).limit(limit).offset(offset)
    )

    return result.all()


async def get_group_by_name(session: AsyncSession, group_name: str) -> Group | None:
    result = await session.execute(select(Group).where(Group.name == group_name))

    return result.scalars().one_or_none()


async def get_group_by_id(session: AsyncSession, group_id: int) -> Group | None:
    result = await session.execute(
        select(Group).where(Group.group_id == group_id, Group.status)
    )

    return result.scalars().one_or_none()


# async def get_group_by_teacher_id(session: AsyncSession, teacher_id: int)-> list[Group]:
#     result = await session.execute(select(Group).where(Group.teacher_id==teacher_id))

#     return result.scalars().all()


# async def update_group(session: AsyncSession, data: UpdateGroup) -> Group:
#     pass


async def student_exclusion_group(
    session: AsyncSession, student_id: int, group_id: int
) -> None:
    result = await session.execute(
        select(StudentGr).where(
            StudentGr.student_id == student_id,
            StudentGr.group_id == group_id,
            StudentGr.status,
        )
    )
    check = result.scalar_one_or_none()
    if not check:
        raise HTTPException(
            status_code=404,
            detail="student bu guruhdan chiqarilgan yoki umuman qo'shilmagan",
        )

    check.status = False
    await session.execute(
        delete(StudentPermissionDate).where(
            StudentPermissionDate.student_id == student_id
        )
    )

    return check

async def update_group(session: AsyncSession,  group_id: int, data: UpdateGroup) -> Group:
    result = await session.execute(select(Group).where(Group.group_id == group_id))
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="guruh topilmadi")
    
    group.name = data.name if data.name else group.name
    group.science_name = data.science_name if data.science_name else group.science_name
    group.price = data.price if data.price else group.price
    group.class_date = data.class_date if data.class_date else group.class_date
    group.class_day = data.class_day if data.class_day else group.class_day

    return group

async def update_group_teacher(session: AsyncSession,  group_id: int, data: UpdateTeacherGroup) -> Group:
    result = await session.execute(select(Group).where(Group.group_id == group_id))
    group = result.scalar_one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="guruh topilmadi")
    
    if data.teacher_id:
        result = await session.execute(select(Teacher).where(Teacher.teacher_id == data.teacher_id))
        teacher = result.scalar_one_or_none()
        if teacher is None:
            raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")

    group.teacher_id = data.teacher_id if data.teacher_id else group.teacher_id
    group.teacher_percent = data.teacher_percent if data.teacher_percent else group.teacher_percent

    return group


async def delete_group(session: AsyncSession, group_id: int) -> None:
    group = await get_group_by_id(session, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="guruh topilmadi")
    
    await session.execute(delete(StudentPermissionDate).where(StudentPermissionDate.group_id==group_id))
    await session.execute(update(StudentDiscount).where(StudentDiscount.group_id==group_id).values(discount_amount=0))
    await session.execute(update(StudentGr).where(StudentGr.group_id==group_id).values(status=False))
    group.status = False
    group.name = f"{group.created_at}{group.name}{datetime}"

    
