from typing import Literal

# Определение допустимых уровней логирования
LogLevels = Literal["DEBUG", "FATAL", "ERROR", "WARN", "INFO"]


# Экпортируемый интерфейс модуля
__all__ = [
    "LogLevels",
]