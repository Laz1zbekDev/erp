from ..db.base import Base
from ..db.session import engine
from .user import User
from .user.admins import Admin
from .user.teachers import Teacher
from .user.students import Student


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
