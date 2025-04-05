import pytest

from pytest_mock import MockFixture
from sqlalchemy import text

from app.cache import clear_cache


@pytest.mark.parametrize(
    "params, expected_status_code, expected_json",
    [
        # Тест на успешный запуск
        ({"n": 2}, 200, {"message": "Процесс скачивания и парсинга запущен на фоне для 2 файлов"}),

        # Тест на отсутствие параметра
        (None, 422, None),

        # Тест на неверное значение параметра
        ({"n": 31}, 422, None),
    ]
)
async def test_fetch_data(client, mocker: MockFixture, params, expected_status_code, expected_json):
    """ Параметризованный тест для эндпоинта fetch_data """

    # мокирование функции
    if params and "n" in params and params["n"] <= 30:
        mocker.patch("app.routes.fetch_and_parse_data")

    response = await client.post("/fetch_data/", params=params)

    assert response.status_code == expected_status_code
    if expected_json:
        assert response.json() == expected_json


@pytest.mark.parametrize(
    "params, expected_status_code, expected_json",
    [
        ({"count": 5}, 200, []),  # Пустая БД
        ({"count": 5}, 200, ["2025-04-03", "2025-04-02"]),  # Данные в БД
        ({"count": 5}, 200, ["2025-04-03", "2025-04-02"]),  # Кэширование данных
        ({"count": 1000}, 200, ["2025-04-03", "2025-04-02"]),  # Большое значение count
    ]
)
async def test_test_get_last_trading_dates(
        client, session, populate_db, mock_cache, params, expected_status_code, expected_json
):
    """ Параметризованный тест для эндпоинта get_last_trading_dates """

    # Если база данных пуста
    result = await session.execute(text("SELECT COUNT(*) FROM spimex_trading_results"))
    count = result.scalar()

    if expected_json == [] and count > 0:  # Если в БД есть данные, очищаем
        await session.execute(text("DELETE FROM spimex_trading_results"))
        await session.commit()
        print("🔥 База данных очищена")

    await clear_cache()

    response = await client.get("/get_last_trading_dates/", params=params)

    assert response.status_code == expected_status_code
    assert response.json() == expected_json


@pytest.mark.parametrize(
    "params, expected_status_code, expected_length, expected_oil_id",
    [
        # Тест на пустой кэш
        ({"start_date": "01-01-2025", "end_date": "31-12-2025", "oil_id": "OIL1", "limit": 10, "offset": 0},
         200, 2, "OIL1"),

        # Тест на кэширование
        ({"start_date": "01-01-2025", "end_date": "31-12-2025", "oil_id": "OIL1", "limit": 10, "offset": 0},
         200, 2, "OIL1"),

        # Тест на фильтры
        ({"start_date": "01-01-2025", "end_date": "31-12-2025", "oil_id": "OIL2", "limit": 10, "offset": 0},
         200, 1, "OIL2"),

        # Тест на пагинацию
        ({"start_date": "01-01-2025", "end_date": "31-12-2025", "oil_id": "OIL1", "limit": 1, "offset": 0},
         200, 1, "OIL1"),
    ]
)
async def test_get_dynamics(
        client, populate_db, mock_cache, params, expected_status_code, expected_length, expected_oil_id
):
    """ Параметризованный тест для эндпоинта get_dynamics """

    mock_get, mock_set = mock_cache or (None, None)

    response = await client.get("/get_dynamics/", params=params)

    assert response.status_code == expected_status_code
    assert len(response.json()) == expected_length

    if expected_length > 0:
        assert response.json()[0]["oil_id"] == expected_oil_id

    mock_set.assert_called_once()


@pytest.mark.parametrize(
    "params, expected_status_code, expected_length, expected_oil_id, expected_delivery_type_id, expected_delivery_basis_id",
    [
        # Тест на фильтрацию
        ({"oil_id": "OIL1", "delivery_type_id": "DT1", "delivery_basis_id": "DB1", "limit": 10, "offset": 0},
         200, 1, "OIL1", "DT1", "DB1"),

        # Тест на кэширование
        ({"start_date": "01-01-2025", "end_date": "31-12-2025", "oil_id": "OIL1", "limit": 10, "offset": 0},
         200, 2, "OIL1", None, None),

        # Тест на пагинацию
        ({"oil_id": "OIL1", "limit": 1, "offset": 0}, 200, 1, "OIL1", None, None),  # Пагинация: первая запись
        ({"oil_id": "OIL1", "limit": 1, "offset": 1}, 200, 1, "OIL1", None, None),  # Пагинация: следующая запись

        # Тест на пустой результат
        ({"oil_id": "OIL3", "limit": 10, "offset": 0}, 200, 0, None, None, None)
    ]
)
async def test_get_trading_results(
        client, populate_db, mock_cache, params, expected_status_code, expected_length, expected_oil_id,
        expected_delivery_type_id, expected_delivery_basis_id
):
    """ Параметризованный тест для эндпоинта get_trading_results """

    mock_get, mock_set = mock_cache or (None, None)

    response = await client.get("/get_trading_results/", params=params)

    assert response.status_code == expected_status_code
    assert len(response.json()) == expected_length

    if expected_length > 0:
        assert response.json()[0]["oil_id"] == expected_oil_id
        if expected_delivery_type_id:
            assert response.json()[0]["delivery_type_id"] == expected_delivery_type_id
        if expected_delivery_basis_id:
            assert response.json()[0]["delivery_basis_id"] == expected_delivery_basis_id

    mock_set.assert_called_once()
