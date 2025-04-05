import os
import aiohttp

from datetime import datetime, timedelta

SAVE_DIR = "spimex_reports"
os.makedirs(SAVE_DIR, exist_ok=True)

BASE_URL = "https://spimex.com/upload/reports/oil_xls/oil_xls_"


async def find_latest_spimex_report(n):
    """ Ищет последний доступный файл, начиная с текущей даты и двигаясь назад """
    today = datetime.today()
    found_files = []

    async with aiohttp.ClientSession() as session:
        for i in range(30):
            date_str = (today - timedelta(days=i)).strftime("%Y%m%d")
            report_url = f"{BASE_URL}{date_str}162000.xls"

            print(f"Проверка файла: {report_url}")

            try:
                async with session.get(report_url, timeout=3) as response:
                    if response.status == 200:
                        print(f"Найден доступный файл: {report_url}")
                        found_files.append(report_url)
                        if len(found_files) >= n:
                            break
                    else:
                        print(f"Файл {report_url} недоступен, статус: {response.status}")
            except aiohttp.ClientError as e:
                print(f"Ошибка при проверке файла {report_url}: {e}")

        return found_files if found_files else None


async def download_spimex_report(report_url):
    """ Скачивает последний найденный отчет """

    filename = os.path.basename(report_url)
    file_path = os.path.join(SAVE_DIR, filename)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(report_url, ssl=False, timeout=3) as response:
                if response.status == 200:
                    with open(file_path, "wb") as file:
                        async for chunk in response.content.iter_chunked(1024):
                            file.write(chunk)
                    print(f"Файл сохранен: {file_path}")
                    return file_path
                else:
                    print(f"Ошибка скачивания: {response.status}")
        except aiohttp.ClientError as e:
            print(f"Ошибка при скачивании файла {report_url}: {e}")

    return None
