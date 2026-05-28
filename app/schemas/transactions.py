from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from ..utils.enums import DiscountType


class StudentTransaction(BaseModel):
    class Student(BaseModel):
        student_id: int
        first_name: str
        last_name: str
        model_config = ConfigDict(from_attributes=True)

    class Admin(BaseModel):
        admin_id: int
        first_name: str
        last_name: str
        model_config = ConfigDict(from_attributes=True)

    class Teacher(BaseModel):
        teacher_id: int
        first_name: str
        last_name: str
        model_config = ConfigDict(from_attributes=True)

    class Group(BaseModel):
        group_id: int
        name: str
        model_config = ConfigDict(from_attributes=True)

    student: Student
    admin: Admin
    teacher: Teacher
    group: Group
    from_when: date
    until_when: date
    created_at: datetime
    amount: Decimal
    center_share: Decimal
    teacher_share: Decimal
    student_discount: int
    discount_type: DiscountType | None

    model_config = ConfigDict(from_attributes=True)


class ResponseStudentTransaction(BaseModel):
    transactions: list[StudentTransaction]
    total_sum: Decimal
    teacher_sum: Decimal
    center_sum: Decimal
    transaction_num: int
    model_config = ConfigDict(from_attributes=True)


class TeacherTransaction(BaseModel):
    class Teacher(BaseModel):
        teacher_id: int
        first_name: str
        last_name: str
        model_config = ConfigDict(from_attributes=True)

    class Admin(BaseModel):
        admin_id: int
        first_name: str
        last_name: str
        model_config = ConfigDict(from_attributes=True)

    teacher: Teacher
    admin: Admin
    created_at: datetime
    amount: int
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class ResponseTeacherTransaction(BaseModel):
    transactions: list[TeacherTransaction]
    total_count: int
    model_config = ConfigDict(from_attributes=True)


class AdminTransaction(BaseModel):
    tr_id: int
    amount: int
    description: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ResponseAdminTransaction(BaseModel):
    transactions: list[AdminTransaction]
    total_count: int
    sum_amount: int
    sum_student: int
    sum_teacher: int
    model_config = ConfigDict(from_attributes=True)


class ResponseSuperadminTransactions(BaseModel):
    class Transactions(AdminTransaction):
        class Admin(BaseModel):
            admin_id: int
            first_name: str
            last_name: str
            model_config = ConfigDict(from_attributes=True)

        admin: Admin
        amount: int
        description: str | None
        created_at: datetime
        model_config = ConfigDict(from_attributes=True)

    transactions: list[Transactions]
    total_count: int
    model_config = ConfigDict(from_attributes=True)
