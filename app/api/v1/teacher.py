from typing import Annotated, Optional

from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Body, HTTPException

from ...depends import get_admin
from ...db.session import get_session
from ...services import get_teacher_by_id, create_teacher
from ...schemas import ResponseTeacher, RegisterTeacher


router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.post("/register", response_model=ResponseTeacher, status_code=201)
async def register_teacher(
    data: RegisterTeacher,
    admin: dict = Depends(get_admin),
    session: AsyncSession = Depends(get_session),
):
    teacher = await create_teacher(session, data)
    await session.commit()
    return teacher
