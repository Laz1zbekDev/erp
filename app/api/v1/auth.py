from typing import Annotated
import asyncio

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ...depends import (
    get_admin,
    get_superadmin,
    get_teacher,
    get_current_user,
)
from ...services import verify_user_id
from ...db import get_session
from ...core import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    verify_password,
    settings,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login_view(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    user_id = form_data.username.strip()
    password = form_data.password.strip()

    if not user_id.isdigit():
        raise HTTPException(status_code=404, detail="bunday user  mavjud emas")
    user = await verify_user_id(session, int(user_id))
    if not user or not user.status:
        raise HTTPException(status_code=404, detail="bunday user  mavjud emas")
    check = verify_password(password, user.hashed_password)
    if not check:
        raise HTTPException(status_code=401, detail="parol xato")

    access_token = create_access_token(
        data={"user_id": user.user_id, "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"user_id": user.user_id, "role": user.role.value}
    )
    print(access_token)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,  # ← sizning refresh token o'zgaruvchingiz nomi
        httponly=True,  # JavaScript o'qiy olmaydi
        secure=False,  # Localhost uchun False, production da True
        samesite="lax",  # CSRF hujumidan himoya
        max_age=60 * 60 * 24 * settings.jwt_refresh_token_expire_days,
    )

    return {
        "access_token": access_token,
        "role": user.role.value,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh_token_view(
    request: Request, response: Response, session: AsyncSession = Depends(get_session)
):
    print("bu funksiya ishlayabdi")
    # 🔹 cookie dan olish
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        print("refresh token topilmadi")
        raise HTTPException(status_code=401, detail="refresh token topilmadi")

    # 🔹 refresh tokenni decode qilish (ALOHIDA funksiyada)
    payload = decode_refresh_token(refresh_token)

    user_id: int = payload.get("user_id")
    role: str = payload.get("role")
    print(role)

    user = await verify_user_id(session, user_id)
    if not user or not user.status or (user.role.value != role):
        print(user.role)
        raise HTTPException(status_code=401, detail="invalid refresh token")
    # 🔹 yangi tokenlar
    new_access_token = create_access_token(data={"user_id": user_id, "role": role})
    new_refresh_token = create_refresh_token(data={"user_id": user_id, "role": role})

    # 🔹 cookie yangilash
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,  # productionda True qil ❗
        samesite="lax",
        max_age=60 * 60 * 24 * settings.jwt_refresh_token_expire_days,
    )

    print("Yangi access token:", new_access_token)
    print("Yangi refresh token:", new_refresh_token)
    return {
        "access_token": new_access_token,
        "role": role,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout_view(response: Response):
    # Logout endpointingizda cookie o'chirilishini tekshiring:
    response.delete_cookie(
        key="refresh_token",
        samesite="lax",  # Bu ham mos bo'lishi kerak
        httponly=True,
    )
    # await asyncio.sleep()
    response.headers["Clear-Site-Data"] = '"cache", "cookies", "storage"'
