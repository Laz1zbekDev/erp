from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    USER = "user"


class DiscountType(Enum):
    TEACHER = "teacher"
    INSTITUTION = "institution"
    BOTH = "both"
