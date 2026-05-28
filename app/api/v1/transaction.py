import asyncio
from typing import Annotated
from datetime import datetime, date, timedelta


from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Body, HTTPException, Query, Path


from ...depends import get_admin
from ...db import get_session
from ...services import (
    get_student_transactions,
    get_teacher_sum,
    sum_student_transactions,
    count_student_transactions,
    get_teacher_transactions,
    count_teacher_transactions,
    get_admin_by_user_id,
    get_admin_transactions,
    count_admin_transactions,
    sum_admin_transactions,
    sum_teacher_transactions,
    create_admin_transaction,
    create_teacher_transaction,
)
from ...schemas import (
    ResponseStudentTransaction,
    ResponseTeacherTransaction,
    ResponseAdminTransaction,
)

router = APIRouter(prefix="/transaction", tags=["transaction"])


@router.get("/student/filter/", response_model=ResponseStudentTransaction)
async def filter_student_transactions_view(
    student_id: Annotated[int | None, Query(ge=1)] = None,
    teacher_id: Annotated[int | None, Query(ge=1)] = None,
    group_id: Annotated[int | None, Query(ge=1)] = None,
    admin_id: Annotated[int | None, Query(ge=1)] = None,
    start: Annotated[datetime | None, Query()] = datetime(
        date.today().year, date.today().month, date.today().day, 0, 0, 0
    ),
    end: Annotated[datetime | None, Query()] = datetime(
        date.today().year, date.today().month, date.today().day, 23, 59, 59
    ),
    limit: Annotated[int | None, Query(ge=1)] = 20,
    offset: Annotated[int | None, Query(ge=0)] = 0,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    transactions = await get_student_transactions(
        session=session,
        student_id=student_id,
        teacher_id=teacher_id,
        group_id=group_id,
        admin_id=admin_id,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )
    total = await sum_student_transactions(
        session,
        start,
        end,
        student_id,
        teacher_id,
        group_id,
        admin_id,
    )
    teacher_sum = await get_teacher_sum(
        session,
        start,
        end,
        student_id,
        teacher_id,
        group_id,
        admin_id,
    )
    center_sum = total - teacher_sum

    transactions_num = await count_student_transactions(
        session,
        start,
        end,
        student_id,
        teacher_id,
        group_id,
        admin_id,
    )

    return ResponseStudentTransaction(
        transactions=transactions,
        total_sum=total,
        teacher_sum=teacher_sum,
        center_sum=center_sum,
        transaction_num=transactions_num,
    )


@router.get("/teacher/filter/", response_model=ResponseTeacherTransaction)
async def get_teacher_transactions_view(
    teacher_id: Annotated[int | None, Query(ge=1)] = None,
    admin_id: Annotated[int | None, Query(ge=1)] = None,
    start: Annotated[datetime | None, Query()] = datetime(
        date.today().year, date.today().month, date.today().day, 0, 0, 0
    ),
    end: Annotated[datetime | None, Query()] = datetime(
        date.today().year, date.today().month, date.today().day, 23, 59, 59
    ),
    limit: Annotated[int | None, Query(ge=1)] = 20,
    offset: Annotated[int | None, Query(ge=0)] = 0,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    transactions = await get_teacher_transactions(
        session, limit, offset, start, end, teacher_id, admin_id
    )
    total = await count_teacher_transactions(session, start, end, teacher_id, admin_id)

    return ResponseTeacherTransaction(transactions=transactions, total_count=total)


@router.post("/teacher/", status_code=204)
async def create_teacher_transaction_view(
    teacher_id: Annotated[int, Query(ge=1)],
    amount: Annotated[int, Query(ge=1, le=100_000_000)],
    description: Annotated[str | None, Query(max_length=555)] = None,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    user_id = admin.get("user_id")
    admin = await get_admin_by_user_id(session, user_id)
    if not admin:
        raise HTTPException(status_code=404, detail="admin topilmadi")

    await create_teacher_transaction(
        session, admin.admin_id, teacher_id, amount, description
    )
    await session.commit()


@router.get("/admin/filter/", response_model=ResponseAdminTransaction)
async def get_admin_transactions_view(
    start: Annotated[datetime | None, Query()] = datetime(
        date.today().year, date.today().month, date.today().day, 0, 0, 0
    ),
    end: Annotated[datetime | None, Query()] = datetime(
        date.today().year, date.today().month, date.today().day, 23, 59, 59
    ),
    limit: Annotated[int | None, Query(ge=1)] = 20,
    offset: Annotated[int | None, Query(ge=0)] = 0,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    user_id = admin.get("user_id")
    admin = await get_admin_by_user_id(session, user_id)
    if not admin:
        raise HTTPException(status_code=404, detail="admin topilmadi")
    transactions = await get_admin_transactions(
        session, start, end, limit, offset, admin.admin_id
    )
    total = await count_admin_transactions(session, start, end, admin.admin_id)
    sum_admin = await sum_admin_transactions(session, start, end, admin.admin_id)
    sum_student = await sum_student_transactions(
        session, start, end, admin_id=admin.admin_id
    )
    sum_teacher = await sum_teacher_transactions(session, start, end, admin.admin_id)
    conflict = sum_student - (sum_admin + sum_teacher)
    return ResponseAdminTransaction(
        transactions=transactions,
        total_count=total,
        sum_amount=sum_admin,
        sum_student=sum_student,
        sum_teacher=sum_teacher,
    )


@router.post("/admin/", status_code=204)
async def create_admin_transaction_view(
    amount: Annotated[int, Query(ge=1, le=100_000_000)],
    description: Annotated[str | None, Query(max_length=555)] = None,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    user_id = admin.get("user_id")
    admin = await get_admin_by_user_id(session, user_id)
    if not admin:
        raise HTTPException(status_code=404, detail="admin topilmadi")

    await create_admin_transaction(session, admin.admin_id, amount, description)
    await session.commit()
