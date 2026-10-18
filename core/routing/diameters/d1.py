"""Точки маршрута D1 с временными описаниями и изображениями.

Шаг пользователя хранится в таблице d1. Первые две точки предлагают
загрузить фотографию; третья содержит поздравление с завершением.
"""

from .base import DiameterRoute, RoutePoint
from .placeholders import IMAGE_PLACEHOLDER


class D1Route(DiameterRoute):
    """Отвечает на выбор D1, используя прогресс из таблицы d1.

    Каждая точка содержит отдельные поля text и image для будущего
    наполнения маршрута. Последний элемент points является финальным.
    """

    diameter = "d1"
    points = (
        RoutePoint(
            text="D1: точка 1. Здесь будет описание первой точки маршрута.",
            image=IMAGE_PLACEHOLDER,
        ),
        RoutePoint(
            text="D1: точка 2. Здесь будет описание второй точки маршрута.",
            image=IMAGE_PLACEHOLDER,
        ),
        RoutePoint(
            text="Поздравляем с прохождением маршрута D1! Здесь будет итоговый текст.",
            image=IMAGE_PLACEHOLDER,
        ),
    )
