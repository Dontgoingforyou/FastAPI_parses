import os
import pytest

from unittest.mock import patch
from app.saver import find_latest_spimex_report, download_spimex_report

TEST_SAVE_DIR = "test_spimex_reports"
os.makedirs(TEST_SAVE_DIR, exist_ok=True)


class TestFindLatestSpimexReport:
    async def test_find_latest_spimex_report_200(self, test_url, mock_spimex_response):
        """ Тест успешного поиска доступных файлов """
        mock_spimex_response.status = 200

        with patch("aiohttp.ClientSession.get", return_value=mock_spimex_response):
            result = await find_latest_spimex_report(1)

        assert result is not None
        assert len(result) == 1
        assert result[0] == test_url

    async def test_find_latest_spimex_report_404(self, mock_spimex_response):
        """ Тест случая, когда файлы не найдены """
        mock_spimex_response.status = 404

        with patch("aiohttp.ClientSession.get", return_value=mock_spimex_response):
            result = await find_latest_spimex_report(5)

        assert result is None


class TestDownloadSpimexReport:

    async def test_download_spimex_report_200(self, test_url, mock_spimex_response):
        """ Тест успешного скачивания отчета """
        mock_spimex_response.status = 200

        with patch("aiohttp.ClientSession.get", return_value=mock_spimex_response):
            result = await download_spimex_report(test_url)

        assert result is not None
        assert os.path.exists(result)

        os.remove(result)

    async def test_test_download_spimex_report_404(self, test_url, mock_spimex_response):
        """ Тест скачивания файла, когда сервер возвращает 404 """
        mock_spimex_response.status = 404
        with patch("aiohttp.ClientSession.get", return_value=mock_spimex_response):
            result = await download_spimex_report(test_url)

        assert result is None

    async def test_test_download_spimex_report_500(self, test_url, mock_spimex_response):
        """ Тест на обработку исключений при скачивании """
        mock_spimex_response.status = 500
        with patch("aiohttp.ClientSession.get", return_value=mock_spimex_response):
            result = await download_spimex_report(test_url)

        assert result is None
