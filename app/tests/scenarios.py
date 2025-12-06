"""\
## Тестовые сценарии для демонстрации логгирования и исключений.

Содержит функции, которые намеренно вызывают ошибки, чтобы показать,
как `AppLogger` и `JsonAppLogger` записывают стек-трейсы и сообщения
разных уровней.
"""

from typing import Iterable

from app.modules.logging import get_app_logger, get_json_app_logger
from .exceptions import AppError, NegativeNumberError, TooBigNumberError


logger = get_app_logger(__name__, level="DEBUG")
json_logger = get_json_app_logger(__name__, level="DEBUG")


def process_numbers(numbers: Iterable[int], *, max_value: int = 5) -> None:
    """\
    ## Обрабатывает числа, демонстрируя разные типы исключений.

    Для каждого числа:

    - логирует DEBUG-сообщение о начале обработки;
    - выбрасывает `NegativeNumberError`, если число отрицательное;
    - выбрасывает `TooBigNumberError`, если число больше `max_value`;
    - логирует INFO при успешной обработке.

    Все исключения перехватываются и логируются с `exc_info=True`.
    """

    for n in numbers:
        logger.debug(f"Начало обработки числа: {n}")
        json_logger.debug(f"Начало обработки числа: {n}")
        try:
            if n < 0:
                raise NegativeNumberError(n)
            if n > max_value:
                raise TooBigNumberError(n, max_value)

            logger.info(f"Число {n} успешно обработано")
            json_logger.info(f"Число {n} успешно обработано")
        except (NegativeNumberError, TooBigNumberError) as err:
            logger.error("Ошибка при обработке числа", exc_info=err)
            json_logger.error("Ошибка при обработке числа", exc_info=err)
        finally:
            logger.debug(f"Завершение обработки числа: {n}")
            json_logger.debug(f"Завершение обработки числа: {n}")


def demo_nested_exceptions() -> None:
    """\
    ## Демонстрирует вложенные исключения и повторное возбуждение.

    Внутренняя функция генерирует `NegativeNumberError`, который
    перехватывается, логируется и оборачивается в `AppError`.
    Снаружи `AppError` снова перехватывается и логируется.
    """

    def inner() -> None:
        try:
            raise NegativeNumberError(-1)
        except NegativeNumberError as err:
            logger.warning("Перехвачена ошибка во внутренней функции", exc_info=err)
            json_logger.warning("Перехвачена ошибка во внутренней функции", exc_info=err)
            raise AppError("Ошибка во внутренней функции") from err

    try:
        inner()
    except AppError as err:
        logger.critical("Критическая ошибка верхнего уровня", exc_info=err)
        json_logger.critical("Критическая ошибка верхнего уровня", exc_info=err)


__all__ = [
    "process_numbers",
    "demo_nested_exceptions",
]
