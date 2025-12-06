"""
## Пакет логгирования приложения.

Содержит реализации текстового логгера (`AppLogger`) и гибридного
`JSON`-логгера (`JsonAppLogger`) с дневной ротацией файлов.
"""

from .text import AppLogger, get_app_logger
from .json import (
	DailyJsonRotatingFileHandler,
	JsonAppLogger,
	JsonLogEntry,
	JsonLogRecord,
	JsonLogReader,
	get_json_app_logger,
)


# Экспортируемый интерфейс модуля
__all__ = [
	"AppLogger",
	"get_app_logger",
	"DailyJsonRotatingFileHandler",
	"JsonLogEntry",
	"JsonAppLogger",
	"get_json_app_logger",
	"JsonLogRecord",
	"JsonLogReader",
]