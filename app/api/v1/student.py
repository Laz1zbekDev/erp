from typing import Annotated, Optional
from datetime import datetime, date, timedelta

from dateutil.relativedelta import relativedelta
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Body, HTTPException, Query, Path


from ...depends import get_admin
from ...utils.enums import DiscountType
from ...db import get_session
from ...models import (
    StudentContact,
    StudentDiscount,
    StudentPermissionDate,
    Group,
)
from ...schemas import (
    RegisterStudent,
    StudentFullResponse,
    ExpiredStudentsResponse,
    ResponseStudent,
    ResonseStudentContact,
    ResponseStudentPermission,
    ResponseAddGroup,
    ResponseStudentDiscount,
)
from ...services import (
    create_student,
    create_student_contact,
    create_student_permission,
    get_groups_by_student,
    create_student_discount,
    get_group_by_id,
    create_student_group,
    get_student_per_and_student,
    get_student_full_info,
    get_student_by_id,
    update_student_name,
    update_student_contact,
    create_student_group,
    get_group_by_id,
    get_student_and_discount,
    update_teacher_salary,
    student_is_group,
    create_student_transactions,
    get_admin_by_user_id,
    update_student_permission,
    get_student_permission,
    upsert_student_discount,
    student_exclusion_group,
    delete_student,
)


router = APIRouter(prefix="/student", tags=["student"])


# @router.get("/", response_model=None)
# async def student_main_view(
#     admin: dict = Depends(get_admin),
#     session: AsyncSession = Depends(get_session),
# ):
#     pass


@router.get("/info/{student_id}", response_model=StudentFullResponse)
async def get_student_full_info_view(
    student_id: Annotated[int, Path(ge=1)],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    check_student = await get_student_by_id(session, student_id)
    if not check_student:
        raise HTTPException(status_code=404, detail="student topilmadi")

    student = await get_student_full_info(session, student_id)
    print(student)
    return {
        "student": student,
        "groups": student.groups,
        "contact": student.contact,
        "discounts": student.student_discount,
        "permissions": student.student_per_dates,
    }


# @router.get("/expired/", response_model=list[ExpiredStudentsResponse])
# async def dashboard_response_view(
#     offset: Annotated[int | None, Query(ge=0, le=100)] = 0,
#     limit: Annotated[int | None, Query(ge=1, le=100)] = 20,
#     admin: dict = Depends(get_admin),
#     session: AsyncSession = Depends(get_session),
# ):

#     result = await get_student_per_and_student(session, offset, limit)
#     response = []
#     today = datetime.now().date()
#     for info in result:
#         expire_date = info.permission_date
#         response.append(
#             {
#                 "student": info.student,
#                 "group_name": info.group.name,
#                 "group_id": info.group.group_id,
#                 "student_contact": info.student.contact.student_number,
#                 "student_parent_contact": info.student.contact.student_parent_number,
#                 "expired_days": (today - expire_date).days,
#             }
#         )

#     return  result


@router.post("/register", response_model=StudentFullResponse, status_code=201)
async def register_view(
    data: Annotated[RegisterStudent, Body()],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    group = await get_group_by_id(session, data.group_id)
    if not group:
        raise HTTPException(status_code=404, detail="guruh topilmadi")
    student = await create_student(session, data)
    student_contact = await create_student_contact(session, student.student_id, data)
    student_per = await create_student_permission(
        session, student.student_id, group.group_id
    )
    student_group = await create_student_group(
        session, student.student_id, data.group_id
    )
    await session.commit()

    return {
        "student": student,
        "groups": [group],
        "contact": student_contact,
        "discounts": None,
        "permissions": [student_per],
    }


@router.post("/add_group/", status_code=201, response_model=ResponseAddGroup)
async def student_add_group(
    student_id: Annotated[int, Query(ge=1)],
    group_id: Annotated[int, Query(ge=1)],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    student = await get_student_by_id(session, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student topilmadi")
    group = await get_group_by_id(session, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="guruh topilmadi")

    student_gr = await create_student_group(session, student_id, group_id)
    permission = await create_student_permission(session, student_id, group_id)
    await session.commit()
    return {
        "group": group,
        "student_per": permission,
        "student": student,
        "discount": None,
    }


@router.put(
    "/student_discount/", status_code=201, response_model=ResponseStudentDiscount
)
async def update_student_discount_view(
    student_id: Annotated[int, Query(ge=1)],
    group_id: Annotated[int, Query(ge=1)],
    discount: Annotated[int, Query(ge=0, le=100)],
    discount_type: Annotated[DiscountType, Query()],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    if discount_type != DiscountType.INSTITUTION and discount_type != DiscountType.BOTH:
        raise HTTPException(
            status_code=400, detail="siz o'qituvchi nomidan chegirma bera olmaysiz"
        )
    discount = await upsert_student_discount(
        session,
        student_id,
        group_id,
        discount,
        discount_type,
    )
    await session.commit()
    await session.refresh(discount)

    return discount


@router.patch("/student_name/{student_id}", response_model=ResponseStudent)
async def update_student_name_view(
    student_id: Annotated[int, Path(ge=1)],
    first_name: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    last_name: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    print(student_id)
    print(type(student_id))

    student = await update_student_name(session, student_id, first_name, last_name)

    return student


@router.patch("/student_contact/{student_id}", response_model=ResonseStudentContact)
async def update_student_contact_view(
    student_id: Annotated[int, Path(ge=1)],
    student_num: Annotated[str | None, Body(min_length=1, max_length=20)] = None,
    student_parent_num: Annotated[str | None, Body(min_length=1, max_length=20)] = None,
    student_telegram: Annotated[str | None, Body(min_length=1, max_length=30)] = None,
    student_parent_telegram: Annotated[
        str | None, Body(min_length=1, max_length=30)
    ] = None,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    print(student_num)
    print(student_parent_num)
    student_contact = await update_student_contact(
        session,
        student_id,
        student_num,
        student_parent_num,
        student_telegram,
        student_parent_telegram,
    )

    return student_contact


@router.patch("/student_per_date/", response_model=ResponseStudentPermission)
async def update_student_permission_date_view(
    student_id: Annotated[int, Query(ge=1)],
    group_id: Annotated[int, Query(ge=1)],
    days: Annotated[int | None, Query()] = None,
    price: Annotated[int | None, Query(ge=1)] = None,
    is_admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    student = await get_student_and_discount(session, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student topilmadi")
    group = await get_group_by_id(session, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="guruh topilmadi")
    check_student_group = await student_is_group(session, student_id, group_id)
    if not check_student_group:
        raise HTTPException(
            status_code=404, detail="bu student bu guruhga tegishli emas"
        )

    admin = await get_admin_by_user_id(session, is_admin.get("user_id"))
    print(admin)
    if not admin:
        raise HTTPException(status_code=404, detail="admin topilmadi")

    student_discount = 0
    discount_type = None
    for discount in student.student_discount:
        if discount.group_id == group_id:
            student_discount = discount.discount_amount
            discount_type = discount.discount_type
            break

    old_per = await get_student_permission(session, student_id, group_id)
    if not old_per:
        raise HTTPException(status_code=404, detail="student vaqti topilmadi")
    if not price:
        price = group.price - student_discount * group.price / 100
    if not days:
        new_date = old_per.permission_date + relativedelta(months=1)
    else:
        new_date = old_per.permission_date + timedelta(days=days)

    teacher_share = 0
    center_share = 0
    if student_discount > 0:
        teacher_share = 0
        center_share = 0

        total_price = (price * 100) / (100 - student_discount)

        if discount_type == DiscountType.TEACHER:
            center_share = total_price * (100 - group.teacher_percent) / 100
            teacher_share = price - center_share
        elif discount_type == DiscountType.INSTITUTION:
            teacher_share = total_price * (group.teacher_percent) / 100
            center_share = price - teacher_share
        else:
            teacher_share = price * group.teacher_percent / 100
            center_share = price - teacher_share
    else:
        teacher_share = price * group.teacher_percent / 100
        center_share = price - teacher_share

    print(price)
    await create_student_transactions(
        session,
        admin.admin_id,
        student_id,
        group_id,
        group.teacher_id,
        old_per.permission_date,
        new_date,
        student_discount,
        discount_type,
        center_share,
        teacher_share,
        price,
    )
    await update_teacher_salary(session, group.teacher_id, teacher_share)
    permission = await update_student_permission(
        session, student_id, group_id, new_date
    )

    await session.commit()
    await session.refresh(permission)

    return permission


@router.delete("/exclusion_group/")
async def exclusion_group_view(
    student_id: Annotated[int, Query(ge=1)],
    group_id: Annotated[int, Query(ge=1)],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    await student_exclusion_group(session, student_id, group_id)
    await session.commit()

    return {"student_id": student_id, "group_id": group_id}


@router.delete("/delete/{student_id}", status_code=204)
async def delate_student_view(
    student_id: Annotated[
        int,
        Path(ge=1),
    ],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    await delete_student(session, student_id)
    await session.commit()
