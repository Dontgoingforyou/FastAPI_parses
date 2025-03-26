import sys

from app import tasks

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import router
from app.tasks import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import create_db
    await create_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)
