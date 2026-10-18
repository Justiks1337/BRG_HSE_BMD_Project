"""Точки маршрута D5 с временными описаниями и изображениями.

Шаг пользователя хранится в таблице d5. Первые две точки предлагают
загрузить фотографию; третья содержит поздравление с завершением.
"""

from .base import DiameterRoute, RoutePoint
from .placeholders import IMAGE_PLACEHOLDER


class D5Route(DiameterRoute):
    """Отвечает на выбор D5, используя прогресс из таблицы d5.

    Каждая точка содержит отдельные поля text и image для будущего
    наполнения маршрута. Последний элемент points является финальным.
    """

    diameter = "d5"
    points = (
        RoutePoint(
            text="D5: точка 1. Здесь будет описание первой точки маршрута.",
            image=IMAGE_PLACEHOLDER,
        ),
        RoutePoint(
            text="D5: точка 2. Здесь будет описание второй точки маршрута.",
            image=IMAGE_PLACEHOLDER,
        ),
        RoutePoint(
            text="Поздравляем с прохождением маршрута D5! Здесь будет итоговый текст.",
            image=IMAGE_PLACEHOLDER,
        ),
    )
