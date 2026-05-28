from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .db.init_db import init_db, wipe_database
from .api.v1 import router as v1_router

app = FastAPI(title="erp")
app.include_router(v1_router)


# 👇 SHU YERGA QO‘SHILADI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def init_db_view():
    # await wipe_database()
    await init_db()


@app.get("/")
async def home_view():
    return "fastapi is running"
