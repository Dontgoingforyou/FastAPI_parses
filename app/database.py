import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv
from app.base import Base

load_dotenv()

POSTGRES_NAME = os.getenv("POSTGRES_NAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"
ADMIN_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"

engine = create_async_engine(DATABASE_URL, echo=True)
admin_engine = create_async_engine(ADMIN_DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    """ Создание БД """

    async with admin_engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        db_exists = await conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{POSTGRES_NAME}'"))
        if not db_exists.scalar():
            await conn.execute(text(f"CREATE DATABASE {POSTGRES_NAME}"))

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """ Создает сессию для работы с БД для взаимодействия с БД """

    async with AsyncSessionLocal() as session:
        yield session
