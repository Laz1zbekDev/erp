from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from passlib.context import CryptContext
from jose import JWTError, jwt, ExpiredSignatureError

from .settings import settings

# password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


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
            raise HTTPException(status_code=401, detail="Invalid token type")

        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, REFRESH_SECRET, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
