from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class LoginUser(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    password: Annotated[str, Field(min_length=4, max_length=50)]
