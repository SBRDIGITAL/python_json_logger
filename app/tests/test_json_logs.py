from pathlib import Path
from pathlib import Path

from app.modules.logging import (
    JsonLogRecord,
    JsonLogReader,
    get_json_app_logger,
)
from app.tests.scenarios import demo_nested_exceptions
from .exceptions import NegativeNumberError


def _last_log_file(logger_name: str) -> Path:
    logs_dir = Path("logs") / logger_name
    # В тестовом проекте ежедневно создаётся один файл, берём последний по имени
    files = sorted(logs_dir.glob("*_logs.ndjson"))
    assert files, "Файл JSON-логов не найден"
    return files[-1]


def test_json_logger_writes_exception_fields(tmp_path: Path) -> None:  # type: ignore[annotation-unchecked]
    """Проверяет, что при `exc_info` в JSON попадают поля об исключении."""

    logger_name = "app.tests.scenarios"
    logger = get_json_app_logger(logger_name, level="DEBUG")

    try:
        raise NegativeNumberError(-42)
    except NegativeNumberError as err:
        logger.error("Ошибка в тесте", exc_info=err)

    log_file = _last_log_file(logger_name)
    reader = JsonLogReader(log_file)
    records = reader.to_records()

    # Берём последнюю запись (с ошибкой)
    last = records[-1]

    assert last.level == "ERROR"
    assert last.exc_type == "NegativeNumberError"
    assert "-42" in (last.exc_message or "")
    # В трейсе должно быть имя исключения и данного файла/модуля
    assert last.exc_traceback is not None
    assert "NegativeNumberError" in last.exc_traceback


def test_json_logger_nested_exceptions(tmp_path: Path) -> None:  # type: ignore[annotation-unchecked]
    """Проверяет, что вложенные исключения также пишутся в JSON-лог."""

    logger_name = "app.tests.scenarios"

    # demo_nested_exceptions использует json_logger с таким именем
    demo_nested_exceptions()

    log_file = _last_log_file(logger_name)
    reader = JsonLogReader(log_file)
    records = reader.to_records()

    # Ищем CRITICAL запись верхнего уровня
    critical_records = [r for r in records if r.level == "CRITICAL"]
    assert critical_records, "Не найдена CRITICAL-запись для вложенного исключения"

    top = critical_records[-1]
    assert top.exc_type == "AppError"
    assert top.exc_message is not None
    assert "AppError" in (top.exc_traceback or "")


def test_json_log_reader_reads_records(tmp_path: Path) -> None:  # type: ignore[annotation-unchecked]
    """Проверяет, что JsonLogReader корректно читает NDJSON-файл и маппит в JsonLogRecord."""

    logger_name = "app.tests.scenarios"
    logger = get_json_app_logger(logger_name, level="DEBUG")
    logger.info("Сообщение 1")
    logger.error("Сообщение 2", exc_info=True)

    log_file = _last_log_file(logger_name)
    reader = JsonLogReader(log_file)
    records = reader.to_records()

    assert isinstance(records, list)
    assert all(isinstance(r, JsonLogRecord) for r in records)
    assert len(records) >= 2
