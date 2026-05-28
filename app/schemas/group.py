from datetime import time, date
from decimal import Decimal
from typing import Annotated, Optional

from pydantic import Field, BaseModel, ConfigDict, model_validator


class CreateGroup(BaseModel):
    teacher_id: Annotated[int, Field(ge=1)]
    science_name: Annotated[str, Field(min_length=1, max_length=100)]
    name: Annotated[str, Field(min_length=1, max_length=100)]
    price: Annotated[int, Field(ge=0, le=1_000_000_0)]
    teacher_percent: Annotated[int, Field(ge=0, le=100)]
    class_day: Annotated[str, Field(min_length=1, max_length=100)]
    class_date: time


# class StudentGroup(BaseModel):
#     student_id: Annotated[int, Field(ge=1)]
#     group_id: Annotated[int, Field(ge=1)]


class UpdateGroup(BaseModel):
    science_name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    name: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    price: Annotated[int | None, Field(ge=1, le=99999999)] = None
    class_day: Annotated[str, Field(min_length=4, max_length=100)] = None
    teacher_percent: Annotated[int | None, Field(ge=0, le=100)] = None
    class_date: time | None = None


class UpdateTeacherGroup(BaseModel):
    teacher_id: Optional[Annotated[int | None, Field(ge=1)]] = None


class ResponseGroup(BaseModel):
    group_id: int
    teacher_id: int
    science_name: str
    name: str
    price: int
    teacher_percent: int
    class_day: str
    class_date: time

    model_config = ConfigDict(from_attributes=True)


class ResponseAllGroup(BaseModel):
    group_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ResponseSearchGroup(BaseModel):
    class GroupResponse(BaseModel):
        class Teacher(BaseModel):
            teacher_id: int
            first_name: str
            last_name: str
            model_config = ConfigDict(from_attributes=True)

        class Group(BaseModel):
            group_id: int
            science_name: str
            name: str
            price: int
            class_day: str
            class_date: time
            model_config = ConfigDict(from_attributes=True)

        group: Group
        teacher: Teacher
        model_config = ConfigDict(from_attributes=True)

    group_num: int
    groups: list[GroupResponse]
    model_config = ConfigDict(from_attributes=True)


class ResponseGroupInfo(BaseModel):
    class Student(BaseModel):
        student_id: int
        first_name: str
        last_name: str

        model_config = ConfigDict(from_attributes=True)

    class PerDates(BaseModel):
        student_id: int
        permission_date: date
        pending_deadline: date

        model_config = ConfigDict(from_attributes=True)

    class Teacher(BaseModel):
        teacher_id: int
        first_name: str
        last_name: str

        model_config = ConfigDict(from_attributes=True)

    group: ResponseGroup
    teacher: Teacher
    student: list[Student]
    permission_dates: list[PerDates]

    model_config = ConfigDict(from_attributes=True)
