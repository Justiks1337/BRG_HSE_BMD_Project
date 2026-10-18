"""Точки маршрута D3 с временными описаниями и изображениями.

Шаг пользователя хранится в таблице d3. Нулевой шаг показывает вступление
с кнопкой «Поехали». Точки 1 и 2 предлагают загрузить фотографию;
точка 3 содержит поздравление с завершением.
"""

from .base import DiameterRoute, RoutePoint
from .placeholders import IMAGE_PLACEHOLDER


class D3Route(DiameterRoute):
    """Отвечает на выбор D3, используя прогресс из таблицы d3.

    introduction содержит пояснение и спойлеры нулевой точки. Каждая
    точка имеет отдельные text и image для будущего наполнения маршрута.
    Последний элемент points является финальным.
    """

    diameter = "d3"
    introduction = RoutePoint(
        text=(
            "D3: знакомство с маршрутом.\n\n"
            "Здесь будет пояснение к маршруту.\n\n"
            "Спойлеры: здесь будет обзор предстоящих точек."
        ),
        image=IMAGE_PLACEHOLDER,
    )
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
