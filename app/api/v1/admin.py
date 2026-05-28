from datetime import date, datetime
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query, Path

from ...depends import get_superadmin, get_admin
from ...schemas import (
    ResponseAdmin,
    RegisterAdmin,
    ResponseSuperadminHome,
    ResponseSuperAdmin,
    ResponseSuperadminTransactions,
)
from ...db import get_session
from ...services import (
    create_admin,
    get_all_admins,
    sum_admin_transactions,
    sum_teacher_transactions,
    sum_student_transactions,
    get_all_admins_and_transactions,
    get_superadmin_by_user_id,
    verify_user_id,
    change_user_password,
    delete_admin,
    get_admin_by_user_id,
    get_admin_transactions,
    count_admin_transactions,
    get_superadmin_transactions,
    count_superadmin_transactions,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/home", response_model=ResponseAdmin)
async def admin_home_view(
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    user_id = admin.get("user_id")
    admin = await get_admin_by_user_id(session, user_id)
    if not admin:
        raise HTTPException(status_code=404, detail="admin topilmadi")
    return admin


@router.get("/all", response_model=list[ResponseAdmin])
async def get_all_admins_view(
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    return await get_all_admins(session, False)


@router.get("/all_admins", response_model=list[ResponseAdmin])
async def get_all_admins_for_superadminview(
    superadmin: dict = Depends(get_superadmin),
    session: AsyncSession = Depends(get_session),
):
    return await get_all_admins(session, True)


@router.get("/superadmin_home")
async def home_view(
    superadmin: dict = Depends(get_superadmin),
    session: AsyncSession = Depends(get_session),
):
    admins = await get_all_admins(session, True)

    response = []
    for admin in admins:
        start = datetime(
            date.today().year, date.today().month, date.today().day, 0, 0, 0
        )
        end = datetime(
            date.today().year, date.today().month, date.today().day, 23, 59, 59
        )
        sum_student = await sum_student_transactions(
            session=session, start=start, end=end, admin_id=admin.admin_id
        )
        sum_teacher = await sum_teacher_transactions(
            session=session, start=start, end=end, admin_id=admin.admin_id
        )
        sum_admin = await sum_admin_transactions(
            session=session, start=start, end=end, admin_id=admin.admin_id
        )
        response.append(
            {
                "admin_id": admin.admin_id,
                "first_name": admin.first_name,
                "last_name": admin.last_name,
                "sum_student": sum_student,
                "sum_teacher": sum_teacher,
                "sum_admin": sum_admin,
            }
        )
    return response


@router.get("/transactions", response_model=ResponseSuperadminTransactions)
async def superadmin_transactions_view(
    limit: Annotated[int | None, Query(ge=1, le=100)] = 20,
    offset: Annotated[int | None, Query(ge=0)] = 0,
    start: Annotated[datetime, Query()] = None,
    end: Annotated[datetime, Query()] = None,
    admin_id: Annotated[int | None, Query(ge=1)] = None,
    superadmin: dict = Depends(get_superadmin),
    session: AsyncSession = Depends(get_session),
):
    transactions = await get_superadmin_transactions(
        session, start, end, limit, offset, admin_id
    )
    transactions_num = await count_superadmin_transactions(
        session, start, end, admin_id
    )

    return ResponseSuperadminTransactions(
        transactions=transactions, total_count=transactions_num
    )


@router.get("/account", response_model=ResponseSuperAdmin)
async def account_view(
    superadmin: dict = Depends(get_superadmin),
    session: AsyncSession = Depends(get_session),
):
    user_id = superadmin.get("user_id")
    superadmin = await get_superadmin_by_user_id(session, user_id)
    if not superadmin:
        raise HTTPException(status_code=404, detail="superadmin topilmadi")
    return superadmin


@router.put("/change_password_superadmin", status_code=204)
async def change_password_superadmin_view(
    new_password: Annotated[str, Query(min_length=6)],
    old_password: Annotated[str, Query(min_length=6)],
    superadmin: dict = Depends(get_superadmin),
    session: AsyncSession = Depends(get_session),
):
    user_id = superadmin.get("user_id")
    await change_user_password(session, user_id, old_password, new_password)
    await session.commit()


@router.put("/change_password", status_code=204)
async def change_password_view(
    new_password: Annotated[str, Query(min_length=6)],
    old_password: Annotated[str, Query(min_length=6)],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    user_id = admin.get("user_id")
    await change_user_password(session, user_id, old_password, new_password)
    await session.commit()


@router.post("/register", response_model=ResponseAdmin, status_code=201)
async def register_admin(
    first_name: Annotated[str, Query(min_length=1, max_length=50)],
    last_name: Annotated[str, Query(min_length=1, max_length=50)],
    password: Annotated[str, Query(min_length=6, max_length=150)],
    superadmin: dict = Depends(get_superadmin),
    session: AsyncSession = Depends(get_session),
):
    data = RegisterAdmin(first_name=first_name, last_name=last_name, password=password)
    admin = await create_admin(session, data)
    await session.commit()
    return admin


@router.delete("/{admin_id}", status_code=204)
async def delete_admin_view(
    admin_id: Annotated[int, Path(ge=1)],
    superadmin: dict = Depends(get_superadmin),
    session: AsyncSession = Depends(get_session),
):
    print(admin_id)
    await delete_admin(session, admin_id)
    await session.commit()
