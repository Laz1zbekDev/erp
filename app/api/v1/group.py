from typing import Annotated, Optional

from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Body, HTTPException, Query, Path

from ...depends import get_admin
from ...db import get_session
from ...schemas import (
    ResponseGroup, 
    CreateGroup, 
    ResponseAllGroup, 
    ResponseGroupInfo,
    UpdateGroup, 
    UpdateTeacherGroup
)
from ...services import (
    get_groups,
    create_group,
    get_group_by_name,
    get_teacher_by_id,
    get_all_groups,
    get_students_by_group,
    delete_group,
    update_group,
    update_group_teacher
)


router = APIRouter(prefix="/group", tags=["group"])


@router.get("/", response_model=list[ResponseGroup])
async def get_groups_view(
    limit: Annotated[int | None, Query(ge=1)] = 20,
    offset: Annotated[int | None, Query(ge=0)] = 0,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    print("bu ishlayabdi")
    return await get_groups(session, limit, offset)


@router.get("/all", response_model=list[ResponseAllGroup])
async def get_all_groups_view(
    limit: Annotated[int | None, Query(ge=1)] = 20,
    offset: Annotated[int | None, Query(ge=0)] = 0,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    print("bu ishlayabdi")
    return await get_all_groups(session)


@router.get("/info/{group_id}", response_model=ResponseGroupInfo)
async def get_group_info_view(
    group_id: Annotated[int, Path(ge=1)],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    group = await get_students_by_group(session, group_id)
    students = group.students
    per_dates = group.student_per_dates

    return {
        "group": group,
        "student": students,
        "permission_dates": per_dates,
    }


@router.post("/create", response_model=ResponseGroup, status_code=201)
async def create_gruup_view(
    group: Annotated[CreateGroup, Body()],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    teacher = await get_teacher_by_id(session, group.teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="o'qituvchi topilmadi")

    check_group_name = await get_group_by_name(session, group.name)
    if check_group_name:
        raise HTTPException(status_code=409, detail="guruh nomi allaqachon ishlatilgan")

    group = await create_group(session, group)
    await session.commit()
    return group


@router.patch("/update/{group_id}", response_model=ResponseGroup)
async def update_group_view(
    group_id: Annotated[int, Path(ge=1)],
    data: Annotated[UpdateGroup, Body()],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    new_group = await update_group(session, group_id, data)
    await session.commit()
    await session.refresh(new_group)

    return new_group

@router.patch("/update_teacher/{group_id}", response_model=ResponseGroup)
async def update_group_teacher_view(
    group_id: Annotated[int, Path(ge=1)],
    data: Annotated[UpdateGroup, Body()],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    new_group = await update_group_teacher(session, group_id, data)
    await session.commit()
    await session.refresh(new_group)

    return new_group


@router.delete("/delete/{group_id}", status_code=204)
async def delete_group_view(
    group_id: Annotated[int, Path(ge=1)],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    await delete_group(session, group_id)

    await session.commit()

    