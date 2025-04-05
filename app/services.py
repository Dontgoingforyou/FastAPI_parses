import asyncio

from app.database import AsyncSessionLocal
from app.saver import download_spimex_report, find_latest_spimex_report
from app.utils import parse_spimex_xlsx


async def fetch_and_parse_data(n: int):
    """ Скачивает и парсит последние отчёты """

    async with AsyncSessionLocal() as db:
        files_to_download = await find_latest_spimex_report(n=n)

        if files_to_download:
            download_files = await asyncio.gather(*[download_spimex_report(url) for url in files_to_download])
            for file in filter(None, download_files):
                print(f"INSIDE FUNC: {parse_spimex_xlsx}")
                print(f"Parsing file: {file}")
                await parse_spimex_xlsx(file, db)
        await db.commit()
