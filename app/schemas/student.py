from typing import Annotated

from pydantic import BaseModel, Field


class RegisterUser(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=4, max_length=50)]
    first_name: Annotated[str, Field(min_length=3, max_length=50)]
    last_name: Annotated[str, Field(min_length=3, max_length=50)]
