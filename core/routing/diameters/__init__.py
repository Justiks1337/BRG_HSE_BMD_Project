"""Обработчики выбора точек маршрутов D1–D5.

Каждый обработчик формирует ResponseProxy по сохранённому шагу пользователя.
Взаимодействие с Telegram остаётся в пакете telegram.
"""

from .d1 import D1Route
from .d2 import D2Route
from .d3 import D3Route
from .d4 import D4Route
from .d5 import D5Route

__all__ = ["D1Route", "D2Route", "D3Route", "D4Route", "D5Route"]
