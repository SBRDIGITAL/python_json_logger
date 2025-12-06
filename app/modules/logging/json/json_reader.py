from __future__ import annotations

from dataclasses import dataclass
from json import loads as json_loads
from pathlib import Path
from typing import Iterator, List


@dataclass(frozen=True)
class JsonLogRecord:
    """\
    ## Представление одной записи `JSON`-лога.

    Поля соответствуют структуре, которую формирует `JsonLogEntry`:

    - `time`: Время события.
    - `logger`: Имя логгера.
    - `level`: Уровень логирования.
    - `file`: Имя файла, вызвавшего лог.
    - `thread`: Имя потока.
    - `message`: Текст сообщения.
    - `exc_type`: Тип исключения, если есть.
    - `exc_message`: Сообщение исключения, если есть.
    - `exc_traceback`: Стек-трейс исключения, если есть.
    """
    time: str
    logger: str
    level: str
    file: str
    thread: str
    message: str
    exc_type: str | None = None
    exc_message: str | None = None
    exc_traceback: str | None = None

    @classmethod
    def from_dict(cls, raw: dict) -> "JsonLogRecord":
        """\
        ## Создаёт `JsonLogRecord` из словаря.

        Args:
            raw (dict): Словарь, полученный из строки `JSON`.

        Returns:
            JsonLogRecord: Инициализированная запись лога.
        """

        return cls(
            time=str(raw.get("time", "")),
            logger=str(raw.get("logger", "")),
            level=str(raw.get("level", "")),
            file=str(raw.get("file", "")),
            thread=str(raw.get("thread", "")),
            message=str(raw.get("message", "")),
            exc_type=(str(raw["exc_type"]) if raw.get("exc_type") is not None else None),
            exc_message=(
                str(raw["exc_message"]) if raw.get("exc_message") is not None else None
            ),
            exc_traceback=(
                str(raw["exc_traceback"]) if raw.get("exc_traceback") is not None else None
            ),
        )


class JsonLogReader:
    """
    ## Утилита для чтения `JSON`-логов в формате NDJSON.

    Ожидается формат файлов, создаваемых `JsonAppLogger`:

    - путь: `logs/<logger_name>/<DD_MM_YY>_logs.json`;
    - каждая строка файла — отдельный корректный `JSON`-объект.
    
    Attributes:
        _path (Path): Путь к файлу лога.
    """
    def __init__(self, file_path: str | Path) -> None:
        """
        ## Инициализирует reader для указанного файла лога.

        Args:
            file_path (str | Path): Путь к `JSON`-файлу лога.
        """

        self._path = Path(file_path)

    def iter_dicts(self) -> Iterator[dict]:
        """
        ## Итерирует лог как последовательность словарей.

        Каждая непустая строка файла парсится функцией `json.loads`.

        Yields:
            dict: Словарь с полями одной записи лога.
        """
        with self._path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield json_loads(line)

    def iter_records(self) -> Iterator[JsonLogRecord]:
        """
        ## Итерирует лог как последовательность `JsonLogRecord`.

        Returns:
            Iterator[JsonLogRecord]: Генератор записей лога.
        """

        for raw in self.iter_dicts():
            yield JsonLogRecord.from_dict(raw)

    def to_list(self) -> List[dict]:
        """
        ## Возвращает все записи лога как список словарей.

        Returns:
            list[dict]: Список всех записей лога.
        """

        return list(self.iter_dicts())

    def to_records(self) -> List[JsonLogRecord]:
        """
        ## Возвращает все записи лога как список `JsonLogRecord`.

        Returns:
            list[JsonLogRecord]: Список всех записей лога.
        """
        return list(self.iter_records())


# Экспортируемый интерфейс модуля
__all__ = [
    "JsonLogRecord",
    "JsonLogReader",
]