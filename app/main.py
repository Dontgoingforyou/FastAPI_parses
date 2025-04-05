from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import create_db
    import asyncio

    await asyncio.sleep(1)
    await create_db()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)
