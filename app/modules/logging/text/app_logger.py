from logging import (
    FileHandler, Formatter, Logger, LogRecord,
    DEBUG, FATAL, ERROR, WARN, INFO, StreamHandler
)
from pathlib import Path
from datetime import datetime

from ..internal import LogLevels



class DailyRotatingFileHandler(FileHandler):
    """
    ## Обработчик логов с ежедневной ротацией файлов.

    Имя файла генерируется динамически на основе текущей даты, что позволяет
    автоматически создавать новый файл при смене дня и немедленно сбрасывать
    буфер после записи.
    """

    def __init__(self, log_dir: Path, encoding: str = "utf-8", mode: str = "a"):
        """
        ## Создаёт обработчик с динамической ротацией по дням.

        Args:
            log_dir (Path): Директория для сохранения логов.
            encoding (str): Кодировка файла. По умолчанию "utf-8".
            mode (str): Режим открытия файла. По умолчанию "a" (добавление).
        """
        self.log_dir = log_dir
        self.encoding = encoding
        self.mode = mode
        self._current_date = None
        self._current_file = None
        
        # Инициализируем родительский класс с временным файлом
        # (он будет заменен при первой записи)
        super().__init__(self._get_current_log_file(), mode, encoding)
    
    def _get_current_log_file(self) -> Path:
        """
        ## Возвращает путь к файлу логов на текущую дату.

        Returns:
            Path: Полный путь к файлу логов.
        """
        current_date = datetime.now().strftime("%d_%m_%y")
        return self.log_dir / f"{current_date}_logs.log"
    
    def emit(self, record: LogRecord) -> None:
        """
        ## Записывает лог-запись, при необходимости меняя файл по дате.

        При смене дня закрывает текущий файл, открывает новый и выполняет
        немедленный сброс буфера после каждой записи.
        """
        try:
            # Получаем актуальный путь файла для текущей даты
            current_log_file = self._get_current_log_file()
            
            # Если дата изменилась - переключаемся на новый файл
            if current_log_file != self._current_file:
                if self.stream:
                    self.stream.close()
                    self.stream = None
                
                self._current_file = current_log_file
                self.baseFilename = str(current_log_file)
                
                # Открываем новый файл
                self.stream = self._open()
            
            # Записываем лог
            super().emit(record)
            
            # Немедленно сбрасываем буфер
            if self.stream:
                self.flush()
        except Exception:
            self.handleError(record)


class AppLogger(Logger):
    """
    ## Логгер приложения с преднастроенной конфигурацией.

    Наследует стандартный `logging.Logger` и используется совместно с
    `get_app_logger` для единообразной настройки логирования.
    """

    def __init__(self, name: str, level: int = INFO):
        """
        ## Инициализирует экземпляр `AppLogger`.

        Args:
            name (str): Имя логгера.
            level (int): Уровень логирования. По умолчанию `INFO`.
        """
        super().__init__(name, level)

    def get_app_logger(self) -> "AppLogger":
        """
        ## Возвращает текущий экземпляр `AppLogger`.

        Returns:
            AppLogger: Экземпляр текущего логгера.
        """
        return self



def get_app_logger(
    logger_name: str,
    level: LogLevels = "INFO",
    to_console: bool = False
) -> AppLogger:
    """
    ## Создаёт и настраивает логгер приложения c файловой ротацией.

    Логи пишутся в каталог `logs/<logger_name>/`. Формат имени файла:
    `DD_MM_YY_logs.log`. Формат сообщения:
    `[Время] [Файл] [Поток] [Уровень] - Сообщение`.

    Args:
        logger_name (str): Имя логгера и подкаталога для логов.
        level (Literal[str]): Уровень логирования ("DEBUG", "FATAL", "ERROR", "WARN", "INFO").
        to_console (bool): Если True, добавляет вывод логов в консоль.

    Returns:
        AppLogger: Настроенный логгер приложения.
    """
    levels_map = {
        "DEBUG": DEBUG,
        "FATAL": FATAL,
        "ERROR": ERROR,
        "WARN": WARN,
        "INFO": INFO,
    }
    current_level: int = levels_map.get(level, INFO)
    
    # Создаем директорию logs если не существует
    log_dir = Path("logs")
    current_dir = log_dir / logger_name
    log_dir.mkdir(exist_ok=True)
    current_dir.mkdir(exist_ok=True)
    
    # Получаем логгер
    logger = AppLogger(logger_name)
    logger.setLevel(current_level)
    
    # Проверяем наличие обработчиков чтобы избежать дублирования
    if not logger.handlers:
        # Создаем обработчик файла с автоматической ротацией по дням
        file_handler = DailyRotatingFileHandler(current_dir, encoding='utf-8')
        file_handler.setLevel(current_level)
        
        # Настраиваем формат сообщения
        log_format = (
            "[%(asctime)s] [%(filename)s] [%(threadName)s] [%(levelname)s] - %(message)s"
        )
        formatter = Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Опционально добавляем StreamHandler для вывода в консоль
        if to_console:
            stream_handler = StreamHandler()
            stream_handler.setLevel(current_level)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
    
    return logger



# Экспортируемый интерфейс модуля
__all__ = [
    "AppLogger",
    "get_app_logger",
]


# Пример использования
if __name__ == "__main__":
    logger = get_app_logger(logger_name='bot', level='DEBUG')
    logger.info("Тестовое сообщение")
    try:
        1 / 0
    except Exception as e:
        logger.error(f"Ошибка в демонстрации: {e}", exc_info=True)