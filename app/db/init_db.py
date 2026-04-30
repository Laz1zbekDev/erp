from sqlalchemy import text


from .session import AsyncSessionLocal
from ..core import settings
from ..services import (
    create_superadmin,
    get_all_superadmins,
    create_admin,
    create_group,
    create_student,
    create_teacher,
)


from .base import Base
from .session import engine
from ..models import *


async def wipe_database():
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))


async def init_db():
    # 1. Jadvallarni yaratish
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. ORM session bilan superadmin yaratish
    async with AsyncSessionLocal() as session:
        superadmins = await get_all_superadmins(session)

        if not superadmins:
            await create_superadmin(
                session,
                settings.superadmin_password,
                settings.superadmin_first_name,
                settings.superadmin_last_name,
            )

        await session.commit()
