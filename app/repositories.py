from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import SpimexTradingResult


async def get_trading_results_query(db: AsyncSession, filters: dict, limit: int, offset: int):
    """ Получение торговых результатов с фильтрацией """

    query = select(SpimexTradingResult).order_by(SpimexTradingResult.date.desc())

    for attr, value in filters.items():
        if value is not None:  # исключение None значении
            query = query.where(getattr(SpimexTradingResult, attr) == value)  # динамическое получение поля из модели

    # Пагинация
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def get_dynamics_query(
        db: AsyncSession,
        start_date: str,
        end_date: str,
        filters: dict,
        limit: int,
        offset: int
):
    """ Получает список торгов за заданный период """

    query = select(SpimexTradingResult).where(
        SpimexTradingResult.date >= start_date,
        SpimexTradingResult.date <= end_date,
    )

    if filters["oil_id"]:
        query = query.where(SpimexTradingResult.oil_id == filters["oil_id"])
    if filters["delivery_type_id"]:
        query = query.where(SpimexTradingResult.delivery_type_id == filters["delivery_type_id"])
    if filters["delivery_basis_id"]:
        query = query.where(SpimexTradingResult.delivery_basis_id == filters["delivery_basis_id"])

    # Пагинация
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()
