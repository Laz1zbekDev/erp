from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException

from ...depends import get_superadmin
from ...schemas import ResponseAdmin, RegisterAdmin
from ...db import get_session
from ...services import create_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/register", response_model=ResponseAdmin, status_code=201)
async def register_admin(
    data: RegisterAdmin,
    superadmin: dict = Depends(get_superadmin),
    session: AsyncSession = Depends(get_session),
):
    admin = await create_admin(session, data)
    await session.commit()
    return admin
