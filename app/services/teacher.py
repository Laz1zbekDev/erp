from decimal import Decimal
from datetime import datetime


from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import literal, select, func, or_, and_
from sqlalchemy.orm import selectinload


from .group import get_group_by_id
from .student import get_groups_by_student, get_student_and_discount
from .user import create_user, change_user_password
from ..models import Teacher, Group, Student, StudentDiscount, Attendance
from ..schemas import RegisterTeacher
from ..utils.enums import UserRole, DiscountType


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


async def get_all_teachers(session: AsyncSession) -> list[Teacher]:
    result = await session.scalars(select(Teacher).where(Teacher.status))

    return result.all()


async def search_teacher(session: AsyncSession, search: str) -> list[Teacher]:
    stmt = select(Teacher).where(Teacher.status)

    if search:
        parts = search.strip().split()
        if len(parts) == 1:
            term = f"%{parts[0]}%"
            stmt = stmt.where(
                or_(Teacher.first_name.ilike(term), Teacher.last_name.ilike(term))
            )
        elif len(parts) >= 2:
            term1 = f"%{parts[0]}%"
            term2 = f"%{parts[1]}%"
            stmt = stmt.where(
                or_(
                    and_(
                        Teacher.first_name.ilike(term1), Teacher.last_name.ilike(term2)
                    ),
                    and_(
                        Teacher.first_name.ilike(term2), Teacher.last_name.ilike(term1)
                    ),
                )
            )

    result = await session.scalars(stmt)
    return list(result.all())


async def get_teacher_and_groups_by_id(session: AsyncSession, teacher_id: int):
    teacher = await session.execute(
        select(Teacher)
        .where(Teacher.teacher_id == teacher_id)
        .options(selectinload(Teacher.groups))
    )
    return teacher.scalar_one_or_none()


async def get_teacher_today_groups(
    session: AsyncSession, teacher_id: int, week_day: str
) -> list[Group]:
    result = await session.execute(
        select(Group)
        .where(Group.teacher_id == teacher_id, Group.status)
        .where(
            literal(week_day.lower())
            == func.any(
                func.string_to_array(
                    func.regexp_replace(
                        func.lower(Group.class_day), r"\s*,\s*", ",", "g"
                    ),
                    ",",
                )
            )
        )
    )
    return result.scalars().all()


async def get_teacher_by_user_id(session: AsyncSession, user_id: int) -> Teacher | None:
    result = await session.execute(
        select(Teacher).where(Teacher.user_id == user_id, Teacher.status)
    )

    return result.scalar_one_or_none()


async def get_teacher_and_students(
    session: AsyncSession,
    teacher_id: int,
) -> Teacher | None:

    student_load = selectinload(Teacher.groups).selectinload(Group.students)

    stmt = (
        select(Teacher)
        .where(Teacher.teacher_id == teacher_id)
        .options(
            student_load.selectinload(Student.contact),
            student_load.selectinload(Student.student_per_dates),
        )
    )

    result = await session.execute(stmt)

    return result.scalar_one_or_none()


async def get_group_today_attandance(
    session: AsyncSession,
    group_id: int
):
    today = datetime.now().date()

    result = await session.execute(
        select(Attendance).where(
            Attendance.group_id == group_id,
            func.date(Attendance.created_at) == today
        )
    )

    return result.one_or_none()



async def get_teacher_discounts(
    session: AsyncSession, teacher_id: int
) -> list[StudentDiscount]:
    result = await session.execute(
        select(StudentDiscount)
        .where(
            StudentDiscount.teacher_id == teacher_id,
            StudentDiscount.discount_amount > 0,
            or_(
                StudentDiscount.discount_type == DiscountType.TEACHER,
                StudentDiscount.discount_type == DiscountType.BOTH,
            ),
        )
        .options(selectinload(StudentDiscount.student))
        .options(selectinload(StudentDiscount.group))
        .order_by(StudentDiscount.created_at.desc())
    )

    return result.scalars().all()


async def create_teacher_discount(
    session: AsyncSession,
    teacher_id: int,
    student_id: int,
    group_id: int,
    discount_amount: int,
) -> None:
    student = await get_student_and_discount(session, student_id)
    if student:
        for discount in student.student_discount:
            if discount.group_id == group_id and discount.teacher_id == teacher_id:
                raise HTTPException(
                    status_code=400, detail="chegirma allaqachon berilgan"
                )
    discount = StudentDiscount(
        teacher_id=teacher_id,
        student_id=student_id,
        group_id=group_id,
        discount_amount=discount_amount,
        discount_type=DiscountType.TEACHER,
    )

    group = await get_group_by_id(session, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="guruh topilmadi")
    if group.teacher_id != teacher_id:
        raise HTTPException(
            status_code=400, detail="o'qituvchi bu guruhga tegishli emas"
        )
    student_groups = await get_groups_by_student(session, student_id)
    for group in student_groups.groups:
        if group.group_id == group_id:
            break
    else:
        raise HTTPException(status_code=400, detail="o'quvchi bu guruhga tegishli emas")
    session.add(discount)
    return discount


async def update_teacher_discount(
    session: AsyncSession,
    student_id: int,
    teacher_id: int,
    group_id: int,
    discount_amount: int,
) -> StudentDiscount:
    studet = await get_student_and_discount(session, student_id)
    if not studet:
        raise HTTPException(status_code=404, detail="o'quvchi topilmadi")
    error = ""
    print(studet.student_discount)
    for discount in studet.student_discount:
        if discount.group_id == group_id:
            if (
                discount.discount_type == DiscountType.TEACHER
                or discount.discount_type == DiscountType.BOTH
            ):
                if discount.teacher_id == teacher_id:
                    discount.discount_amount = discount_amount
                    return discount
                else:
                    error += "o'qituvchi bu chegirmaga tegishli emas"
            else:
                error += "bu chegirma o'qituvchi tomonidan berilmagan"
        else:
            error += "o'quvchi bu guruhga tegishli emas"
    raise HTTPException(status_code=400, detail=error)


async def update_teacher_password(
    session: AsyncSession, teacher_id: int, new_password: str, password: str
) -> None:
    teacher = await get_teacher_by_id(session, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")
    await change_user_password(session, teacher.user_id, password, new_password)


async def update_teacher_salary(
    session: AsyncSession, teacher_id: int, price: int
) -> Teacher:
    teacher = await get_teacher_by_id(session, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")

    teacher.salary += Decimal(str(price))

    return teacher


async def update_teacher_name(
    session: AsyncSession,
    teacher_id: int,
    first_name: str | None,
    last_name: str | None,
):
    teacher = await get_teacher_by_id(session, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")
    teacher.first_name = first_name if first_name else teacher.first_name
    teacher.last_name = last_name if last_name else teacher.last_name
    return teacher


async def delete_teacher(session: AsyncSession, teacher_id: int) -> None:
    teacher = await get_teacher_and_groups_by_id(session, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")

    teacher_groups = [group for group in teacher.groups if group.status]
    if teacher_groups:
        raise HTTPException(
            status_code=400, detail="O'qitvuchining faol guruhlari mavjud"
        )

    user = await session.execute(
        select(Teacher).where(Teacher.teacher_id == teacher_id)
    )
    user = user.scalar_one_or_none()
    if user:
        user.status = False
    teacher.status = False
