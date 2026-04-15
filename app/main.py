from fastapi import FastAPI

from .models.init_db import init_db
from .api.v1 import router as v1_router

app = FastAPI(title="iticket")
app.include_router(v1_router)


@app.on_event("startup")
async def init_db_view():
    await init_db()


@app.get("/")
async def home_view():
    return "fastapi is running"
