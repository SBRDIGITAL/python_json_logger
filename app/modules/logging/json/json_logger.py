from __future__ import annotations

from dataclasses import asdict, dataclass
from json import dumps as json_dumps
from logging import (
    DEBUG,
    ERROR,
    FATAL,
    INFO,
    WARN,
    Formatter,
    LogRecord,
    Logger,
    StreamHandler,
)
from logging import FileHandler
from pathlib import Path
from datetime import datetime

from ..internal import LogLevels



class DailyJsonRotatingFileHandler(FileHandler):
    """
    ## Обработчик логов с ежедневной ротацией и `JSON`-форматом.

    Имя файла генерируется динамически на основе текущей даты в формате
    `DD_MM_YY_logs.json` внутри каталога, соответствующего имени логгера.

    Формат записи — одна `JSON`-строка на строку файла (NDJSON):

    ```json
    {"time": "...", "logger": "...", "level": "...", "file": "...", ...}
    ```
    """
    def __init__(self,
        log_dir: Path,
        encoding: str = "utf-8",
        mode: str = "a"
    ) -> None:
        """
        ## Создаёт обработчик с дневной ротацией и `JSON`-записью.

        Args:
            log_dir (Path): Директория для сохранения логов.
            encoding (str): Кодировка файла. По умолчанию `"utf-8"`.
            mode (str): Режим открытия файла. По умолчанию `"a"` (добавление).
        """
        self.log_dir = log_dir
        self.encoding = encoding
        self.mode = mode
        self._current_file: Path | None = None

        super().__init__(self._get_current_log_file(), mode, encoding)

    def _get_current_log_file(self) -> Path:
        """
        ## Возвращает путь к `JSON`-файлу логов на текущую дату.

        Returns:
            Path: Полный путь к файлу логов.
        """
        current_date = datetime.now().strftime("%d_%m_%y")
        return self.log_dir / f"{current_date}_logs.ndjson"

    def emit(self, record: LogRecord) -> None:  # type: ignore[override]
        """
        ## Записывает лог-запись в `JSON`-формате с ежедневной ротацией.

        При смене дня закрывает текущий файл, открывает новый и выполняет
        немедленный сброс буфера после каждой записи.
        """
        try:
            current_log_file = self._get_current_log_file()

            if current_log_file != self._current_file:
                if self.stream:
                    self.stream.close()
                    self.stream = None

                self._current_file = current_log_file
                self.baseFilename = str(current_log_file)
                self.stream = self._open()

            json_line = self._serialize_record(record)
            stream = self.stream or self._open()
            stream.write(json_line + "\n")
            stream.flush()
        except Exception:
            self.handleError(record)

    @staticmethod
    def _serialize_record(record: LogRecord) -> str:
        """
        ## Преобразует `LogRecord` в `JSON`-строку.

        Поля близки по смыслу к форматированию в `AppLogger` и
        дополняются данными об исключении, если оно есть:

        - `time`: Время события.
        - `logger`: Имя логгера.
        - `level`: Уровень логирования.
        - `file`: Имя файла, вызвавшего лог.
        - `thread`: Имя потока.
        - `message`: Текст сообщения.
        - `exc_type`: Тип исключения (класс), если есть.
        - `exc_message`: Сообщение исключения, если есть.
        - `exc_traceback`: Стек-трейс в текстовом виде, если есть.
        """
        payload = JsonLogEntry.from_record(record)
        return json_dumps(asdict(payload), ensure_ascii=False, default=str)


@dataclass
class JsonLogEntry:
    """
    ## Структура записи лога в `JSON`-формате.

    Используется `dataclass` для явного описания полей и их назначения.
    
    Attributes:
        time (str): Время события.
        logger (str): Имя логгера.
        level (str): Уровень логирования.
        file (str): Имя файла, вызвавшего лог.
        thread (str): Имя потока.
        message (str): Текст сообщения.
        exc_type (str | None): Имя класса исключения.
        exc_message (str | None): Сообщение исключения.
        exc_traceback (str | None): Стек-трейс исключения.
    """
    time: str
    logger: str
    level: str
    file: str
    thread: str
    message: str
    exc_type: str | None
    exc_message: str | None
    exc_traceback: str | None

    @classmethod
    def from_record(cls, record: LogRecord) -> "JsonLogEntry":
        """
        ## Строит `JsonLogEntry` из экземпляра `LogRecord`.

        Args:
            record (LogRecord): Запись стандартного логгера.

        Returns:
            JsonLogEntry: Готовая структура для сериализации в `JSON`.
        """
        formatter = Formatter()
        time = formatter.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S")

        exc_type: str | None = None
        exc_message: str | None = None
        exc_traceback: str | None = None

        if record.exc_info:
            etype, evalue, etb = record.exc_info
            if etype is not None:
                exc_type = etype.__name__
            if evalue is not None:
                exc_message = str(evalue)
            try:
                from traceback import format_exception

                exc_traceback = "".join(format_exception(etype, evalue, etb))
            except Exception:
                exc_traceback = None

        return cls(
            time=time,
            logger=record.name,
            level=record.levelname,
            file=record.filename,
            thread=record.threadName,
            message=record.getMessage(),
            exc_type=exc_type,
            exc_message=exc_message,
            exc_traceback=exc_traceback,
        )


class JsonAppLogger(Logger):
    """
    ## Логгер приложения с `JSON`-выводом и дневной ротацией.

    Наследует стандартный `logging.Logger` и используется совместно с
    `get_json_app_logger` для единообразной настройки структурированного
    логирования.
    
    Attributes:
        name (str): Имя логгера.
        level (int): Уровень логирования.
    """
    def __init__(self, name: str, level: int = INFO) -> None:
        """
        ## Инициализирует экземпляр `JsonAppLogger`.

        Args:
            name (str): Имя логгера.
            level (int): Уровень логирования. По умолчанию `INFO`.
        """
        super().__init__(name, level)

    def get_logger(self) -> "JsonAppLogger":
        """
        ## Возвращает текущий экземпляр `JsonAppLogger`.

        Returns:
            JsonAppLogger: Экземпляр текущего логгера.
        """
        return self


def get_json_app_logger(
    logger_name: str,
    level: LogLevels = "INFO",
    to_console: bool = False,
) -> JsonAppLogger:
    """
    ## Создаёт и настраивает `JSON`-логгер с дневной ротацией файлов.

    Логи пишутся в каталог `logs/<logger_name>/`. Формат имени файла:
    `DD_MM_YY_logs.json`. Каждая строка файла — отдельный `JSON`-объект
    с полями `time`, `logger`, `level`, `file`, `thread`, `message`.

    Args:
        logger_name (str): Имя логгера и подкаталога для логов.
        level (LogLevels): Уровень логирования ("DEBUG", "FATAL",
            "ERROR", "WARN", "INFO").
        to_console (bool): Если `True`, добавляет вывод логов в консоль
            в текстовом виде.

    Returns:
        JsonAppLogger: Настроенный `JSON`-логгер приложения.
    """
    levels_map = {
        "DEBUG": DEBUG,
        "FATAL": FATAL,
        "ERROR": ERROR,
        "WARN": WARN,
        "INFO": INFO,
    }
    current_level: int = levels_map.get(level, INFO)

    log_dir = Path("logs")
    current_dir = log_dir / logger_name
    log_dir.mkdir(exist_ok=True)
    current_dir.mkdir(exist_ok=True)

    logger = JsonAppLogger(logger_name)
    logger.setLevel(current_level)

    if not logger.handlers:
        file_handler = DailyJsonRotatingFileHandler(current_dir, encoding="utf-8")
        file_handler.setLevel(current_level)
        logger.addHandler(file_handler)

        if to_console:
            log_format = (
                "[%(asctime)s] [%(filename)s] [%(threadName)s] "
                "[%(levelname)s] - %(message)s"
            )
            formatter = Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
            stream_handler = StreamHandler()
            stream_handler.setLevel(current_level)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

    return logger


# Экспортируемый интерфейс модуля
__all__ = [
    "DailyJsonRotatingFileHandler",
    "JsonLogEntry",
    "JsonAppLogger",
    "get_json_app_logger",
]


if __name__ == "__main__":
    test_logger = get_json_app_logger(
        logger_name="__main__",
        level="DEBUG",
        to_console=True
    )
    test_logger.info("Тестовое JSON-сообщение")