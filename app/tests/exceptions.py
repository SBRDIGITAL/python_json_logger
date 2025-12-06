"""\
## Кастомные исключения для демонстрации логгирования.

Содержит иерархию исключений, которые используются в тестовых
сценариях модуля `main`.
"""


class AppError(Exception):
    """\
    ## Базовое исключение приложения.

    От него наследуются все специфичные для приложения ошибки.
    """


class NegativeNumberError(AppError):
    """\
    ## Ошибка, возникающая при обнаружении отрицательного числа.
    """

    def __init__(self, value: int) -> None:
        msg = f"Отрицательное число недопустимо: {value}"
        super().__init__(msg)
        self.value = value


class TooBigNumberError(AppError):
    """\
    ## Ошибка, возникающая при превышении максимального допустимого значения.
    """

    def __init__(self, value: int, limit: int) -> None:
        msg = f"Число {value} превышает максимально допустимое значение {limit}"
        super().__init__(msg)
        self.value = value
        self.limit = limit


__all__ = [
    "AppError",
    "NegativeNumberError",
    "TooBigNumberError",
]
