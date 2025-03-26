import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.saver import download_spimex_report, find_latest_spimex_report
from app.utils import parse_spimex_xlsx


async def fetch_and_parse_data(db: AsyncSession, n: int):
    """ Скачивает и парсит последние отчёты """

    files_to_download = await find_latest_spimex_report(n=n)

    if files_to_download:
        download_files = await asyncio.gather(*[download_spimex_report(url) for url in files_to_download])

        for file in filter(None, download_files):
            await parse_spimex_xlsx(file, db)
