from decimal import Decimal
from datetime import date, datetime, time
from typing import Annotated, Optional

from pydantic import BaseModel, Field, ConfigDict

from ..utils.enums import DiscountType


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


class ResponseSearchTeacher(BaseModel):
    class Teacher(ResponseTeacher):
        created_at: datetime

        model_config = ConfigDict(from_attributes=True)

    teacher_num: int
    teachers: list[Teacher]


class ResponseTeacherInfo(BaseModel):
    class Group(BaseModel):
        group_id: int
        name: str
        price: int
        teacher_percent: int

        model_config = ConfigDict(from_attributes=True)

    class Teacher(ResponseTeacher):
        salary: Decimal
        created_at: datetime
        user_id: int

        model_config = ConfigDict(from_attributes=True)

    teacher: Teacher
    groups: list[Group]

    model_config = ConfigDict(from_attributes=True)


class ResponseTeacherHome(BaseModel):
    class Group(BaseModel):
        group_id: int
        name: str
        class_date: time
        model_config = ConfigDict(from_attributes=True)

    teacher: ResponseTeacher
    groups: list[Group]

    model_config = ConfigDict(from_attributes=True)


class ResponseTeacherPeyments(BaseModel):
    class TeacherPayment(BaseModel):
        class Admin(BaseModel):
            first_name: str
            last_name: str
            model_config = ConfigDict(from_attributes=True)

        amount: int
        created_at: datetime
        description: str | None
        admin: Admin

        model_config = ConfigDict(from_attributes=True)

    payments_num: int
    teacher_payments: list[TeacherPayment]

    model_config = ConfigDict(from_attributes=True)


class ResponseTeacherGrops(BaseModel):
    class Group(BaseModel):
        name: str
        price: int
        teacher_percent: int
        class_day: str
        class_date: time

        model_config = ConfigDict(from_attributes=True)

    groups_num: int
    groups: list[Group]

    model_config = ConfigDict(from_attributes=True)


class ResponseTeacherStudents(BaseModel):
    class Group(BaseModel):
        class Student(BaseModel):
            class Contact(BaseModel):
                student_number: str
                student_parent_number: str

                model_config = ConfigDict(from_attributes=True)

            class StudentPermissionDate(BaseModel):
                group_id: int
                permission_date: datetime
                pending_deadline: datetime

                model_config = ConfigDict(from_attributes=True)


            student_id: int
            first_name: str
            last_name: str
            contact: Contact
            student_per_dates: list[StudentPermissionDate]

            model_config = ConfigDict(from_attributes=True)

        group_id: int
        name: str
        students: list[Student]

        model_config = ConfigDict(from_attributes=True)

    students_num: int
    groups: list[Group]

    model_config = ConfigDict(from_attributes=True)


class ResponseTeacherDiscounts(BaseModel):
    class StudentDiscounts(BaseModel):
        class Student(BaseModel):
            student_id: int
            first_name: str
            last_name: str

            model_config = ConfigDict(from_attributes=True)

        class Group(BaseModel):
            group_id: int
            name: str

            model_config = ConfigDict(from_attributes=True)

        discount_amount: int
        discount_type: DiscountType
        student: Student
        group: Group

        model_config = ConfigDict(from_attributes=True)

    discounts_num: int
    discounts: list[StudentDiscounts]

    model_config = ConfigDict(from_attributes=True)


class ResponseTeacherGroupStudents(BaseModel):
    class Student(BaseModel):
        first_name: str
        last_name: str
        student_id: int

        model_config = ConfigDict(from_attributes=True)

    class Group(BaseModel):
        group_id: int
        name: str

        model_config = ConfigDict(from_attributes=True)
    
    group: Group
    students: list[Student]

    model_config = ConfigDict(from_attributes=True)