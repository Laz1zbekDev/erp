from datetime import datetime
import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, Request, Query, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ...depends import get_admin
from ...db import get_session
from ...schemas import DashboardResponse
from ...services import (
    all_group_number,
    all_student_number,
    all_teacher_number,
    get_student_per_and_student,
    update_student_pending,
    count_student_per_and_student,
    sum_student_transactions,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardResponse)
async def dashboard_response_view(
    offset: Annotated[int | None, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1)] = 20,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    students = await all_student_number(session)
    teachers = await all_teacher_number(session)
    groups = await all_group_number(session)
    # today_income = await get_today_income(session)

    total_expire = await count_student_per_and_student(session)
    result = await get_student_per_and_student(session, offset, limit)
    start = datetime(
        datetime.now().year, datetime.now().month, datetime.now().day, 0, 0, 0
    )
    end = datetime(
        datetime.now().year, datetime.now().month, datetime.now().day, 23, 59, 59
    )
    today_income = await sum_student_transactions(session, start, end)
    response = []
    today = datetime.now().date()
    for info in result:
        expire_date = info.permission_date
        response.append(
            {
                "student": info.student,
                "group_name": info.group.name,
                "group_id": info.group.group_id,
                "student_contact": info.student.contact.student_number,
                "student_parent_contact": info.student.contact.student_parent_number,
                "expired_days": (today - expire_date).days,
            }
        )

    return {
        "sudent_num": students,
        "teacher_num": teachers,
        "group_num": groups,
        "today_income": today_income,
        "total_expire": total_expire,
        "expire_students": response,
    }


@router.patch("/pending/")
async def student_permission_pending(
    student_id: Annotated[int, Query()],
    group_id: Annotated[int, Query()],
    days: Annotated[int, Query()],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):

    result = await update_student_pending(session, student_id, group_id, days)
    return {"student_id": result.student_id}
