from .group import (
    CreateGroup,
    ResponseGroup,
    ResponseAllGroup,
    ResponseGroupInfo,
    UpdateGroup,
    UpdateTeacherGroup
)
from .student import (
    RegisterStudent,
    ResponseStudent,
    StudentFullResponse,
    ResonseStudentContact,
    ResponseStudentDiscount,
    ResponseStudentPermission,
    ExpiredStudentsResponse,
    ResponseAddGroup,
)
from .teacher import RegisterTeacher, ResponseTeacher
from .admin import (
    RegisterAdmin,
    ResponseAdmin,
)
from .dashboard import DashboardResponse
from .user import LoginUser
