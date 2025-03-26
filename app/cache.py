from redis.asyncio import Redis
import json
from datetime import datetime, timedelta, date

redis = None


async def get_redis():
    """ Подключение к Redis """

    global redis
    if not redis:
        redis = await Redis.from_url("redis://redis:6379")
    return redis


async def get_cached_data(key: str):
    """ Получение данных из кэша """

    r = await get_redis()
    data = await r.get(key)
    return json.loads(data) if data else None


async def set_cached_data(key: str, value):
    """ Сохранение данных в кэш до 14:11 """

    def date_converter(obj):
        """ Функция для сериализации объектов типа "date" """

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()  # Преобразует в строку ISO 8601
        raise TypeError(f"Тип {obj.__class__.__name__} не сериализуется")

    r = await get_redis()
    now = datetime.now()
    reset_time = now.replace(hour=14, minute=11, second=0, microsecond=0)

    # Если текущее время больше или равно 14:11, устанавливается сброс на следующий день
    if now >= reset_time:
        reset_time += timedelta(days=1)

    expire_seconds = (reset_time - now).total_seconds()
    await r.set(key, json.dumps(value, default=date_converter), ex=int(expire_seconds))


async def clear_cache():
    """ Очистка всего кэша в 14:11 """

    r = await get_redis()
    await r.flushdb()
