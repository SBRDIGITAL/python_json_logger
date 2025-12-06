"""Корневой пакет приложения.

Экспортирует подмодуль `modules` для удобных импортов вида
`from app.modules.logging import ...`.
"""

from . import modules

__all__ = ["modules"]