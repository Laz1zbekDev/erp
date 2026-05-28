import asyncio
from typing import Annotated, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Body, HTTPException, Query, Path, Request, BackgroundTasks

from app.schemas.teacher import ResponseTeacherGrops

from ...utils.sms_service import send_sms
from ...depends import get_admin, get_teacher, get_week_day
from ...db import get_session
from ...services import (
    get_teacher_by_id,
    create_teacher,
    get_all_teachers,
    search_teacher,
    get_teacher_and_groups_by_id,
    get_teacher_today_groups,
    get_teacher_by_user_id,
    delete_teacher,
    update_teacher_salary,
    update_teacher_name,
    get_teacher_transactions,
    count_teacher_transactions,
    get_teacher_and_students,
    get_teacher_discounts,
    get_group_today_attandance,
    get_students_by_group,
    get_group_by_id,
    create_teacher_discount,
    update_teacher_password,
    update_teacher_discount,
)
from ...schemas import (
    ResponseTeacher,
    RegisterTeacher,
    ResponseSearchTeacher,
    ResponseTeacherInfo,
    ResponseTeacherHome,
    ResponseTeacherPeyments,
    ResponseTeacherStudents,
    ResponseTeacherDiscounts,
    ResponseTeacherGroupStudents,
)


router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.get("/", response_model=ResponseSearchTeacher)
async def get_teachers_view(
    limit: Annotated[int | None, Query(ge=1, le=100)] = 20,
    offset: Annotated[int | None, Query(ge=0)] = 0,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    teachers = await get_all_teachers(session)
    teachers_num = len(teachers)
    teachers = teachers[offset : offset + limit]

    return {
        "teacher_num": teachers_num,
        "teachers": teachers,
    }


@router.get("/all", response_model=list[ResponseTeacher])
async def get_all_teachers_view(
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    teachers = await get_all_teachers(session)

    return teachers


@router.get("/info/{teacher_id}", response_model=ResponseTeacherInfo)
async def get_teacher_info_view(
    teacher_id: Annotated[int, Path(ge=1)],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    teacher = await get_teacher_and_groups_by_id(session, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")
    groups = teacher.groups
    return {
        "teacher": teacher,
        "groups": [group for group in groups if group.status],
    }


@router.get("/search", response_model=ResponseSearchTeacher)
async def search_teacher_view(
    search: Annotated[str, Query(max_length=100)],
    offset: Annotated[int | None, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=100)] = 20,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    teachers = await search_teacher(session, search)
    teachers_num = len(teachers)
    teachers = teachers[offset : offset + limit]

    return {
        "teacher_num": teachers_num,
        "teachers": teachers,
    }


@router.get("/teacher_home", response_model=ResponseTeacherHome)
async def teacher_home_view(
    teacher_check: dict = Depends(get_teacher),
    session: AsyncSession = Depends(get_session),
    week_day: str = get_week_day(),
):
    user_id = teacher_check.get("user_id")
    print(user_id)
    teacher = await get_teacher_by_user_id(session, user_id)
    print(teacher)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")
    teacher_groups = await get_teacher_today_groups(
        session, teacher.teacher_id, week_day
    )

    return ResponseTeacherHome(teacher=teacher, groups=teacher_groups)


@router.get("/teacher_peyments", response_model=ResponseTeacherPeyments)
async def teacher_peyments_view(
    limit: Annotated[int | None, Query(ge=1, le=100)] = 20,
    offset: Annotated[int | None, Query(ge=0)] = 0,
    teacher_check: dict = Depends(get_teacher),
    session: AsyncSession = Depends(get_session),
):
    user_id = teacher_check.get("user_id")
    teacher = await get_teacher_by_user_id(session, user_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")

    teacher_payments = await get_teacher_transactions(
        session=session, teacher_id=teacher.teacher_id, limit=limit, offset=offset
    )
    payments_num = await count_teacher_transactions(
        session=session, teacher_id=teacher.teacher_id
    )
    print(payments_num)
    return {
        "payments_num": payments_num,
        "teacher_payments": teacher_payments,
    }


@router.get("/teacher_groups", response_model=ResponseTeacherGrops)
async def get_teacher_groups_view(
    offset: Annotated[int | None, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=100)] = 20,
    teacher_check: dict = Depends(get_teacher),
    session: AsyncSession = Depends(get_session),
):
    user_id = teacher_check.get("user_id")
    teacher = await get_teacher_by_user_id(session, user_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")

    teacher_groups = await get_teacher_and_groups_by_id(session, teacher.teacher_id)
    groups = [group for group in teacher_groups.groups if group.status]
    groups_num = len(groups)
    groups = groups[offset : offset + limit]

    return ResponseTeacherGrops(groups_num=groups_num, groups=groups)


@router.get("/teacher_students", response_model=ResponseTeacherStudents)
async def get_teacher_students_view(
    teacher_check: dict = Depends(get_teacher),
    session: AsyncSession = Depends(get_session),
):
    user_id = teacher_check.get("user_id")
    teacher = await get_teacher_by_user_id(session, user_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")
    teacher_and_students = await get_teacher_and_students(session, teacher.teacher_id)
    # bu yerda faqat statusi True bo'lgan guruhlar olinyabdi
    groups = [group for group in teacher_and_students.groups if group.status]
    students = []
    for group in groups:
        # bu yerda faqat statusi true bo'lgan studentlar olinyabdi
        group.students = [i for i in group.students if i.status]
        for student in group.students:
            # bu yerda studentning ko'plab permission date lari ichidan faqat ushbu guruhga tegishli bo'lganlari olinyabdi
            student.student_per_dates = [per_date for per_date in student.student_per_dates if per_date.group_id == group.group_id]

        students.extend(group.students)
    students_num = len(students)

    return ResponseTeacherStudents(
        students_num=students_num,
        groups=groups,
    )


@router.get("/teacher_discounts", response_model=ResponseTeacherDiscounts)
async def get_teacher_discounts_view(
    teacher_check: dict = Depends(get_teacher),
    session: AsyncSession = Depends(get_session),
):
    user_id = teacher_check.get("user_id")
    teacher = await get_teacher_by_user_id(session, user_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")
    teacher_discounts = await get_teacher_discounts(session, teacher.teacher_id)

    return ResponseTeacherDiscounts(
        discounts_num=len(teacher_discounts), discounts=teacher_discounts
    )

@router.get("/group_students", response_model=ResponseTeacherGroupStudents)
async def get_group_students_view(
    group_id: Annotated[int, Query(ge=1)],
    teacher: dict = Depends(get_teacher),
    session: AsyncSession = Depends(get_session),
):
    today_attandance = await get_group_today_attandance(session, group_id)
    if today_attandance:
        return {"message": "ok"}
    
    group = await get_students_by_group(session, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="guruh topilmadi")
    
    return ResponseTeacherGroupStudents(group=group, students=group.students)
    

@router.post("/create_teacher_discount", status_code=204)
async def create_teacher_discount_view(
    student_id: Annotated[int, Query(ge=1)],
    group_id: Annotated[int, Query(ge=1)],
    discount_amount: Annotated[int, Query(ge=0)],
    teacher_check: dict = Depends(get_teacher),
    session: AsyncSession = Depends(get_session),
):
    user_id = teacher_check.get("user_id")
    teacher = await get_teacher_by_user_id(session, user_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")

    await create_teacher_discount(
        session, teacher.teacher_id, student_id, group_id, discount_amount
    )
    await session.commit()


@router.put("/update_teacher_discount", status_code=204)
async def update_teacher_discount_view(
    student_id: Annotated[int, Query(ge=1)],
    group_id: Annotated[int, Query(ge=1)],
    discount_amount: Annotated[int, Query(ge=0)],
    teacher_check: dict = Depends(get_teacher),
    session: AsyncSession = Depends(get_session),
):
    user_id = teacher_check.get("user_id")
    teacher = await get_teacher_by_user_id(session, user_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")

    await update_teacher_discount(
        session, student_id, teacher.teacher_id, group_id, discount_amount
    )
    await session.commit()


@router.patch("/update_teacher_password", status_code=204)
async def update_teacher_password_view(
    new_password: Annotated[str, Query(min_length=6)],
    password: Annotated[str, Query(min_length=6)],
    teacher_check: dict = Depends(get_teacher),
    session: AsyncSession = Depends(get_session),
):
    user_id = teacher_check.get("user_id")
    teacher = await get_teacher_by_user_id(session, user_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")

    await update_teacher_password(session, teacher.teacher_id, new_password, password)
    await session.commit()


@router.patch("/add_salary/")
async def add_salary_view(
    teacher_id: Annotated[int, Query(ge=1)],
    price: Annotated[int, Query(ge=1, le=100000000)],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    teacher = await update_teacher_salary(session, teacher_id, price)
    await session.commit()
    return {"teacher_id": teacher_id, "salary": teacher.salary}


@router.patch("/update_name/", response_model=ResponseTeacherInfo.Teacher)
async def update_teacher_name_view(
    teacher_id: Annotated[int, Query(ge=1)],
    first_name: Annotated[str | None, Query(max_length=50)],
    last_name: Annotated[str | None, Query(max_length=50)],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    teacher = await update_teacher_name(session, teacher_id, first_name, last_name)
    await session.commit()
    return teacher


@router.post("/register", response_model=ResponseTeacher, status_code=201)
async def register_teacher_view(
    data: RegisterTeacher,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    teacher = await create_teacher(session, data)
    await session.commit()
    return teacher


@router.post("/send_sms", status_code=201)
async def send_sms_view(
    data: dict,
    background_tasks: BackgroundTasks,
    teacher: dict = Depends(get_teacher),
    session: AsyncSession = Depends(get_session),
):
    user_id = teacher.get("user_id")
    teacher = await get_teacher_by_user_id(session, user_id)
    group = await get_group_by_id(session, data.get("group_id"))
    if not group:
        raise HTTPException(status_code=404, detail="guruh topilmadi")
    if group.teacher_id != teacher.teacher_id:
        raise HTTPException(
            status_code=400, detail="o'qituvchi bu guruhga tegishli emas"
        )
    today_attandance = await get_group_today_attandance(session, group.group_id)
    if today_attandance:
        return {"message": "ok"}
    background_tasks.add_task(send_sms, session, data)
    return 
    


@router.delete("/delete/{teacher_id}", status_code=204)
async def delete_teacher_view(
    teacher_id: Annotated[int, Path(ge=1)],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    await delete_teacher(session, teacher_id)
    await session.commit()
    return {"message": "O'qituvchi muvaffaqiyatli o'chirildi"}
