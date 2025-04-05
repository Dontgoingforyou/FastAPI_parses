import pytest
import asyncio

from datetime import datetime
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from pytest_mock import MockerFixture
from sqlalchemy import text

from app.database import engine, MODE, AsyncSessionLocal
from app.main import app
from app.models import Base


@pytest.fixture(autouse=True)
async def clean_db(setup_db, session):
    """ Очищает таблицу перед каждым тестом """

    # Логирование текущее состояние базы данных перед очисткой
    result = await session.execute(text("SELECT * FROM spimex_trading_results"))
    records = result.fetchall()
    print(f"🌱 Существующие записи в базе данных перед очисткой: {records}")

    print("🔁 Отчистка БД перед тестом")
    await session.execute(text("TRUNCATE TABLE spimex_trading_results RESTART IDENTITY CASCADE;"))
    await session.commit()

    # Логирование состояние базы данных после очистки
    result = await session.execute(text("SELECT * FROM spimex_trading_results"))
    records = result.fetchall()
    print(f"✅ База данных очищена. Записи после очистки: {records}")


@pytest.fixture(scope="session")
def event_loop():
    """ Создание глобального event loop для всех async-тестов """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def populate_db(session):
    """ Фикстура для добавления данных в БД """
    from app.models import SpimexTradingResult
    from datetime import date, datetime

    print("🌱 Заполнение базы данных тестовыми данными")

    test_data = [
        SpimexTradingResult(
            exchange_product_id="1",
            exchange_product_name="Нефть",
            oil_id="OIL1",
            delivery_basis_id="DB1",
            delivery_basis_name="Базис 1",
            delivery_type_id="DT1",
            volume=1000.0,
            total=500000.0,
            count=10,
            date=date(2025, 4, 3),
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        SpimexTradingResult(
            exchange_product_id="2",
            exchange_product_name="Дизель",
            oil_id="OIL1",
            delivery_basis_id="DB2",
            delivery_basis_name="Базис 2",
            delivery_type_id="DT2",
            volume=800.0,
            total=400000.0,
            count=8,
            date=date(2025, 4, 2),
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        # Эта запись будет удовлетворять фильтру
        SpimexTradingResult(
            exchange_product_id="3",
            exchange_product_name="Газ",
            oil_id="OIL2",
            delivery_basis_id="DB3",
            delivery_basis_name="Базис 3",
            delivery_type_id="DT3",
            volume=900.0,
            total=450000.0,
            count=9,
            date=date(2025, 4, 3),
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
    ]

    session.add_all(test_data)
    await session.commit()
    print("✅ БД заполнена")


@pytest.fixture(autouse=True)
async def setup_db():
    assert MODE == "TEST"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session():
    """Создание сессии для тестов"""
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_spimex_response():
    """ Фикстура для создания мок-ответа """

    mock_response = AsyncMock()
    mock_response.__aenter__.return_value = mock_response  # Это для асинхронного контекстного менеджера

    async def mock_iter_chunked(size):
        """ Мокает асинхронный итератор для iter_chunked """
        yield b'chunk1'
        yield b'chunk2'

    mock_response.content.iter_chunked = mock_iter_chunked
    return mock_response


@pytest.fixture
def test_url():
    """ Фикстура для создания тестового URL """

    test_date = datetime.today().strftime("%Y%m%d")
    return f"https://spimex.com/upload/reports/oil_xls/oil_xls_{test_date}162000.xls"


@pytest.fixture
def mock_cache(mocker: MockerFixture):
    """Фикстура для мокирования кэша"""

    mock_get = mocker.patch("app.routes.get_cached_data", autospec=True)
    mock_set = mocker.patch("app.routes.set_cached_data", autospec=True)

    # Настраиваем поведение
    mock_get.return_value = None
    mock_set.return_value = None

    return mock_get, mock_set


@pytest.fixture
def mock_spimex_dependencies():
    """Фикстура для мокирования зависимостей в fetch_and_parse_data"""

    with patch("app.services.find_latest_spimex_report", new_callable=AsyncMock) as mock_find_reports, \
            patch("app.services.download_spimex_report", new_callable=AsyncMock) as mock_download, \
            patch("app.services.parse_spimex_xlsx", new_callable=AsyncMock) as mock_parse:
        print(f"Mocking dependencies: {mock_find_reports}, {mock_download}, {mock_parse}")
        yield mock_find_reports, mock_download, mock_parse
