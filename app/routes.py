from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.cache import get_cached_data, set_cached_data
from app.database import get_db
from datetime import date
from typing import List, Optional

from app.models import SpimexTradingResult
from app.repositories import get_trading_results_query, get_dynamics_query
from app.services import fetch_and_parse_data
from app.schemas import SpimexTradingResultResponse, SpimexTradingResultQuery


router = APIRouter(prefix="", tags=["Эндпоинты"])


@router.post("/fetch_data/")
async def fetch_data(
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
        n: Optional[int] = Query(ge=1, le=30, description="Количество файлов для скачивания")
):
    """ Запускает процесс скачивания и парсинга данных в фоне """

    background_tasks.add_task(fetch_and_parse_data, db, n)
    return {"message": f"Процесс скачивания и парсинга запущен на фоне для {n} файлов"}


@router.get("/get_last_trading_dates/", response_model=List[date])
async def get_last_trading_dates(
        count: int = Query(description="Количество дней для поиска"),
        db: AsyncSession = Depends(get_db)
):
    """ Возвращает список последних торговых дней из БД с кэшированием """

    cache_key = f"last_trading_dates:{count}"
    cached_data = await get_cached_data(cache_key)

    if cached_data:
        return cached_data

    result = await db.execute(
        select(SpimexTradingResult.date)
        .distinct()
        .order_by(SpimexTradingResult.date.desc())
        .limit(count)
    )
    data = [row[0] for row in result.all()]

    await set_cached_data(cache_key, data)
    return data


@router.get("/get_dynamics/", response_model=List[SpimexTradingResultResponse])
async def get_dynamics(
        query: SpimexTradingResultQuery = Depends(),
        oil_id: Optional[str] = None,
        delivery_type_id: Optional[str] = None,
        delivery_basis_id: Optional[str] = None,
        limit: int = Query(10, le=100, description="Количество данных на одной странице"),
        offset: int = Query(0, description="С какой записи начать выборку данных"),
        db: AsyncSession = Depends(get_db),
):
    """
    Список торгов за заданный период с кэшированием
    - `start_date` (формат: DD-MM-YYYY) — начальная дата выборки
    - `end_date` (формат: DD-MM-YYYY) — конечная дата выборки
    """
    start_date = query.start_date
    end_date = query.end_date

    filters = {
        "oil_id": oil_id,
        "delivery_type_id": delivery_type_id,
        "delivery_basis_id": delivery_basis_id,
    }

    cache_key = f"get_dynamics:{start_date}:{end_date}:{oil_id}:{delivery_type_id}:{delivery_basis_id}:{limit}:{offset}"
    cached_data = await get_cached_data(cache_key)

    if cached_data:
        return cached_data

    data = await get_dynamics_query(db, start_date, end_date, filters, limit, offset)
    data_pydantic = [SpimexTradingResultResponse.model_validate(item) for item in data]

    await set_cached_data(cache_key, [item.model_dump() for item in data_pydantic])
    return data_pydantic


@router.get("/get_trading_results/", response_model=List[SpimexTradingResultResponse])
async def get_trading_results(
        oil_id: Optional[str] = None,
        delivery_type_id: Optional[str] = None,
        delivery_basis_id: Optional[str] = None,
        limit: int = Query(10, le=100, description="Количество данных на одной странице"),
        offset: int = Query(0, description="С какой записи начать выборку данных"),
        db: AsyncSession = Depends(get_db),
):
    """ Список последних торгов с кэшированием """

    filters = {
        "oil_id": oil_id,
        "delivery_type_id": delivery_type_id,
        "delivery_basis_id": delivery_basis_id,
    }

    cache_key = f"get_trading_results:{oil_id}:{delivery_type_id}:{delivery_basis_id}:{limit}:{offset}"
    cached_data = await get_cached_data(cache_key)

    if cached_data:
        return cached_data

    data = await get_trading_results_query(db, filters, limit, offset)
    data_pydantic = [SpimexTradingResultResponse.model_validate(item) for item in data]

    await set_cached_data(cache_key, [item.model_dump() for item in data_pydantic])
    return data_pydantic
