from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession


from app.core import decode_access_token
from app.services import verify_user_id
from app.db import get_session
from app.utils.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> dict:
    check = decode_access_token(token)
    user_id = check.get("user_id")
    print(type(user_id))
    if not user_id or not isinstance(user_id, int):
        raise HTTPException(status_code=403, detail="token invalid")
    return check


async def get_admin(
    payload: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    print("get admin ishladi")
    check = await verify_user_id(session, payload.get("user_id"))
    if not check or check.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Siz admin emassiz",
        )
    

    return payload


async def get_superadmin(
    payload: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    print(payload)
    check = await verify_user_id(session, payload.get("user_id"))
    print(check)
    print(payload.get("user_id"))
    if not check or check.role != UserRole.SUPERADMIN:
        print("bazadan topilmadi")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Siz superadmin emassiz",
        )
    return payload


async def get_teacher(
    payload: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    check = await verify_user_id(session, payload.get("user_id"))
    if not check or check.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Siz o'qituvchi emassiz",
        )
    return payload


def get_week_day():
    days = [
        "Dushanba",
        "Seshanba",
        "Chorshanba",
        "Payshanba",
        "Juma",
        "Shanba",
        "Yakshanba",
    ]

    today = datetime.today()

    return days[today.weekday()]
