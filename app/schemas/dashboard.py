from typing import Annotated

from pydantic import BaseModel, Field

from .student import ExpiredStudentsResponse


class DashboardResponse(BaseModel):
    sudent_num: int
    teacher_num: int
    group_num: int
    today_income: int
    total_expire: int
    expire_students: list[ExpiredStudentsResponse]
