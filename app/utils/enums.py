from enum import Enum


class UserRole(Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    TEACHER = "teacher"


class DiscountType(Enum):
    TEACHER = "o'qituvchi"
    INSTITUTION = "markaz"
    BOTH = "umumiy"


class SmsStatus(Enum):
    pass