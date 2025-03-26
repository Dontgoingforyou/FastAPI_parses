import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.cache import clear_cache

scheduler = AsyncIOScheduler()
scheduler.add_job(clear_cache, "cron", hour=14, minute=11)

# Запуск планировщика только если код выполняется не в тестах
if "pytest" not in sys.modules:
    scheduler.start()
