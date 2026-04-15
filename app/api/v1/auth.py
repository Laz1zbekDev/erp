from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register():
    return "hi"
