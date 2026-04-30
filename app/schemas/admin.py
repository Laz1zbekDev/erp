from typing import Annotated

from pydantic import BaseModel, Field


class RegisterAdmin(BaseModel):
    password: Annotated[str, Field(min_length=6, max_length=150)]
    first_name: Annotated[str, Field(min_length=1, max_length=50)]
    last_name: Annotated[str, Field(min_length=1, max_length=50)]


class ResponseAdmin(BaseModel):
    admin_id: int
    user_id: int
    first_name: str
    last_name: str
