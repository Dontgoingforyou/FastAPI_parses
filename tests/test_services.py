from unittest import mock

import pytest

from app.services import fetch_and_parse_data


@pytest.mark.parametrize(
    "mock_find_reports_return, mock_download_side_effect, expected_download_calls, expected_parse_calls",
    [
        (
                ["http://test.com/file1.xlsx", "http://test.com/file2.xlsx"],  # оба файла скачиваются
                ["file1.xlsx", None],  # один файл скачивается, второй нет
                2,  # download будет вызван два раза
                ["file1.xlsx"]  # парсинг будет только для одного файла
        ),
        (
                ["http://test.com/file1.xlsx"],  # один файл
                [None],  # Файл не скачивается
                1,  # Ожидаем, что download будет вызван 1 раз
                []  # парсинга не будет, он принял ислам
        ),
        (
                [],  # нет отчетов
                [],  # ничего не скачивается
                0,  # download не будет вызван
                []  # парсинг не будет вызван, так как нет отчетов
        ),
    ]
)
async def test_fetch_and_parse_data(
        mock_spimex_dependencies, mock_find_reports_return,
        mock_download_side_effect, expected_download_calls, expected_parse_calls
):
    """ Тест успешной работы fetch_and_parse_data с параметризацией """

    mock_find_reports, mock_download, mock_parse = mock_spimex_dependencies

    mock_find_reports.return_value = mock_find_reports_return
    mock_download.side_effect = mock_download_side_effect

    print(f"MOCK FUNC: {mock_parse}")

    await fetch_and_parse_data(2)

    mock_find_reports.assert_awaited_once_with(n=2)
    assert mock_download.await_count == expected_download_calls

    for url in mock_find_reports_return:
        mock_download.assert_any_await(url)

    if expected_parse_calls:
        for file in expected_parse_calls:
            print(f"Expected file for parsing: {file}")
            mock_parse.assert_any_await(file, mock.ANY)
    else:
        mock_parse.assert_not_awaited()
    print(f"Mock parse calls: {mock_parse.mock_calls}")

