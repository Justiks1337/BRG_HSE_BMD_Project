"""Точки маршрута D2 с временными описаниями и изображениями.

Шаг пользователя хранится в таблице d2. Первые две точки предлагают
загрузить фотографию; третья содержит поздравление с завершением.
"""

from .base import DiameterRoute, RoutePoint
from .placeholders import IMAGE_PLACEHOLDER


class D2Route(DiameterRoute):
    """Отвечает на выбор D2, используя прогресс из таблицы d2.

    Каждая точка содержит отдельные поля text и image для будущего
    наполнения маршрута. Последний элемент points является финальным.
    """

    diameter = "d2"
    points = (
        RoutePoint(
            text="D2: точка 1. Здесь будет описание первой точки маршрута.",
            image=IMAGE_PLACEHOLDER,
        ),
        RoutePoint(
            text="D2: точка 2. Здесь будет описание второй точки маршрута.",
            image=IMAGE_PLACEHOLDER,
        ),
        RoutePoint(
            text="Поздравляем с прохождением маршрута D2! Здесь будет итоговый текст.",
            image=IMAGE_PLACEHOLDER,
        ),
    )
