from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from jose import JWTError, jwt, ExpiredSignatureError

from .settings import settings


# jwt token handling
ACCESS_SECRET = settings.jwt_secret_key_access
REFRESH_SECRET = settings.jwt_secret_key_refresh
ALGORITHM = settings.jwt_algorithm


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update(
        {
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.jwt_access_token_expire_minutes),
            "type": "access",
        }
    )
    return jwt.encode(to_encode, ACCESS_SECRET, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update(
        {
            "exp": datetime.now(timezone.utc)
            + timedelta(days=settings.jwt_refresh_token_expire_days),
            "type": "refresh",
        }
    )
    return jwt.encode(to_encode, REFRESH_SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, ACCESS_SECRET, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            print("bu token access token emas")
            raise HTTPException(
                status_code=401,
                detail={
                    "error_code": "TOKEN_INVALID",  # ← frontend shu ni o'qiydi
                    "message": "Access token noto'g'ri",
                },
            )

        return payload

    except ExpiredSignatureError:
        print("access token muddati tugagan")
        raise HTTPException(status_code=401, detail="access token muddati tugagan")
    except JWTError:
        print("access token noto'g'ri")
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": "TOKEN_INVALID",  # ← frontend shu ni o'qiydi
                "message": "Access token noto'g'ri",
            },
        )


def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, REFRESH_SECRET, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            print("bu token refresh token emas")
            raise HTTPException(
                status_code=401,
                detail={
                    "error_code": "TOKEN_INVALID",  # ← frontend shu ni o'qiydi
                    "message": "Access token noto'g'ri",
                },
            )
        return payload

    except ExpiredSignatureError:
        print("refresh token muddati tugagan")
        raise HTTPException(status_code=401, detail="refresh token muddati tugagan")
    except JWTError:
        print("refresh token noto'g'ri")
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": "TOKEN_INVALID",  # ← frontend shu ni o'qiydi
                "message": "Access token noto'g'ri",
            },
        )
