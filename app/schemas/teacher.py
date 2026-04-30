from decimal import Decimal
from typing import Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict


class RegisterTeacher(BaseModel):
    password: Annotated[str, Field(min_length=6, max_length=150)]
    first_name: Annotated[str, Field(min_length=1, max_length=50)]
    last_name: Annotated[str, Field(min_length=1, max_length=50)]


class ResponseTeacher(BaseModel):
    teacher_id: int
    user_id: int
    first_name: str
    last_name: str
    salary: Decimal

    model_config = ConfigDict(from_attributes=True)
