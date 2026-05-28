import asyncio
from datetime import date, time
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
    ResponseSearchGroup,
    ResponseGroupInfo,
    UpdateGroup,
    UpdateTeacherGroup,
)
from ...services import (
    get_groups,
    create_group,
    get_group_by_name,
    get_teacher_by_id,
    get_all_groups,
    get_students_by_group,
    get_all_science,
    delete_group,
    update_group,
    update_group_teacher,
    search_groups,
)


router = APIRouter(prefix="/group", tags=["group"])


@router.get("/", response_model=ResponseSearchGroup)
async def get_groups_view(
    limit: Annotated[int | None, Query(ge=1)] = 20,
    offset: Annotated[int | None, Query(ge=0)] = 0,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):

    groups = await get_groups(session)
    response_group = []
    group_num = len(groups)

    paginated_groups = groups[offset : offset + limit]
    for group in paginated_groups:
        response_group.append(
            {
                "group": group,
                "teacher": group.teacher,
            }
        )

    return {
        "group_num": group_num,
        "groups": response_group,
    }


@router.get("/all", response_model=list[ResponseAllGroup])
async def get_all_groups_view(
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):

    return await get_all_groups(session)


@router.get("/info/{group_id}", response_model=ResponseGroupInfo)
async def get_group_info_view(
    group_id: Annotated[int, Path(ge=1)],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    group = await get_students_by_group(session, group_id)

    return {
        "group": group,
        "teacher": group.teacher,
        "student": group.students,
        "permission_dates": group.student_per_dates,
    }


@router.get("/science", response_model=list[ResponseGroup])
async def get_all_science_view(
    admin: dict = Depends(get_admin), session: AsyncSession = Depends(get_session)
):
    return await get_all_science(session)


@router.get("/search/", response_model=ResponseSearchGroup)
async def search_group_view(
    group_name: Annotated[str | None, Query(max_length=100)] = None,
    teacher_id: Annotated[int | None, Query(ge=1)] = None,
    group_day: Annotated[str | None, Query(max_length=100)] = None,
    group_date: Annotated[time | None, Query()] = None,
    science_name: Annotated[str | None, Query(max_length=100)] = None,
    offset: Annotated[int | None, Query(ge=0)] = 0,
    limit: Annotated[int | None, Query(ge=1, le=100)] = 20,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    groups = await search_groups(
        session, group_name, teacher_id, group_day, group_date, science_name
    )
    response_group = []
    group_num = len(groups)

    paginated_groups = groups[offset : offset + limit]
    for group in paginated_groups:
        response_group.append(
            {
                "group": group,
                "teacher": group.teacher,
            }
        )

    return {
        "group_num": group_num,
        "groups": response_group,
    }


@router.post("/create", status_code=201)
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
    await session.refresh(group)

    return group.group_id


@router.patch("/update/{group_id}", response_model=ResponseGroup)
async def update_group_view(
    group_id: Annotated[int, Path(ge=1)],
    data: Annotated[UpdateGroup, Body()],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    print(data.teacher_percent)
    new_group = await update_group(session, group_id, data)
    await session.commit()
    await session.refresh(new_group)

    return new_group


@router.patch("/update_teacher/", response_model=ResponseGroup)
async def update_group_teacher_view(
    group_id: Annotated[int, Query(ge=1)],
    teacher_id: Annotated[int, Query(ge=1)],
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    new_group = await update_group_teacher(session, group_id, teacher_id)
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
