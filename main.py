"""
Точка входа и небольшая демонстрация возможностей логгера.

Запускает простую обработку чисел и тестовые сценарии из
`app.tests.scenarios`, которые генерируют различные пользовательские
исключения и показывают, как они пишутся в `.log` и `.ndjson`.
"""

from pathlib import Path

from app.modules.logging import JsonLogReader, get_app_logger, get_json_app_logger
from app.tests.scenarios import demo_nested_exceptions, process_numbers


logger = get_app_logger(__name__, level="DEBUG")
json_logger = get_json_app_logger(__name__, level="DEBUG")


def main() -> None:
    """
    ## Точка входа приложения.

    1. Логирует простую последовательность чисел.
    2. Запускает `process_numbers` с заведомо проблемными значениями.
    3. Запускает `demo_nested_exceptions` для демонстрации вложенных
       исключений и повторного возбуждения.
    """
    numbers_list = [i for i in range(10 + 1)]
    for n in numbers_list:
        logger.debug(f"Current number: {n}")
        json_logger.debug(f"Current number: {n}")

    # Демонстрация сценариев с реальными кастомными исключениями
    process_numbers([0, 1, -1, 3, 10], max_value=5)
    demo_nested_exceptions()

    # Динамическое чтение всех NDJSON-логов из корневой директории logs
    logs_root = Path("logs")
    ndjson_files = sorted(logs_root.rglob("*.ndjson"))
    all_records: list = []
    for file_path in ndjson_files:
        reader = JsonLogReader(file_path)
        all_records.extend(reader.to_records())

    print("NDJSON files found:", ndjson_files)
    print("Total JsonLogRecord objects:", len(all_records))
    print("Records sample:", all_records)

    print("Hello from python_json_logger!")


if __name__ == "__main__":
    main()
