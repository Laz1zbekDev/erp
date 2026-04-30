from fastapi import APIRouter

from .auth import router as auth_router
from .group import router as group_router
from .teacher import router as teacher_router
from .student import router as student_router
from .admin import router as admin_router
from .dashboard import router as dashboard_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(group_router)
router.include_router(teacher_router)
router.include_router(student_router)
router.include_router(admin_router)
router.include_router(dashboard_router)
