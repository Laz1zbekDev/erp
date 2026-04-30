from datetime import datetime, date
from typing import Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict

from ..utils.enums import DiscountType
from .group import ResponseGroup


class RegisterStudent(BaseModel):
    first_name: Annotated[str, Field(min_length=3, max_length=50)]
    last_name: Annotated[str, Field(min_length=3, max_length=50)]
    group_id: Annotated[int, Field(ge=1)]
    student_number: Annotated[str, Field(min_length=1, max_length=20)]
    student_parent_number: Annotated[str, Field(min_length=1, max_length=20)]
    student_telegram: Optional[
        Annotated[str | None, Field(min_length=1, max_length=30)]
    ] = None
    student_parent_telegram: Optional[
        Annotated[str | None, Field(min_length=1, max_length=30)]
    ] = None


class ResponseStudent(BaseModel):
    student_id: int
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class ResonseStudentContact(BaseModel):
    contact_id: int
    student_number: str
    student_parent_number: str
    student_telegram: str | None
    student_parent_telegram: str | None

    model_config = ConfigDict(from_attributes=True)


class ResponseStudentPermission(BaseModel):
    permission_date_id: int
    student_id: int
    group_id: int
    permission_date: date
    pending_deadline: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResponseStudentDiscount(BaseModel):
    discount_id: int
    student_id: int
    teacher_id: int
    group_id: int
    discount_amount: int
    discount_type: DiscountType

    model_config = ConfigDict(from_attributes=True)


class StudentFullResponse(BaseModel):
    student: ResponseStudent
    groups: list[ResponseGroup]
    contact: ResonseStudentContact
    discounts: list[ResponseStudentDiscount] | None = None
    permissions: list[ResponseStudentPermission]

    model_config = ConfigDict(from_attributes=True)


class ExpiredStudentsResponse(BaseModel):
    student: ResponseStudent
    group_name: str
    group_id: int
    student_contact: str
    student_parent_contact: str
    expired_days: int


class ResponseAddGroup(BaseModel):
    group: ResponseGroup
    student_per: ResponseStudentPermission
    student: ResponseStudent
    discount: ResponseStudentDiscount | None = None
