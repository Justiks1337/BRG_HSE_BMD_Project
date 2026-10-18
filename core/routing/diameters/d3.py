"""Точки маршрута D3 с временными описаниями и изображениями.

Шаг пользователя хранится в таблице d3. Первые две точки предлагают
загрузить фотографию; третья содержит поздравление с завершением.
"""

from .base import DiameterRoute, RoutePoint
from .placeholders import IMAGE_PLACEHOLDER


class D3Route(DiameterRoute):
    """Отвечает на выбор D3, используя прогресс из таблицы d3.

    Каждая точка содержит отдельные поля text и image для будущего
    наполнения маршрута. Последний элемент points является финальным.
    """

    diameter = "d3"
    points = (
        RoutePoint(
            text="D3: точка 1. Здесь будет описание первой точки маршрута.",
            image=IMAGE_PLACEHOLDER,
        ),
        RoutePoint(
            text="D3: точка 2. Здесь будет описание второй точки маршрута.",
            image=IMAGE_PLACEHOLDER,
        ),
        RoutePoint(
            text="Поздравляем с прохождением маршрута D3! Здесь будет итоговый текст.",
            image=IMAGE_PLACEHOLDER,
        ),
    )
