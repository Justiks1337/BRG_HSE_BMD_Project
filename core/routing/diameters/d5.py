"""Точки маршрута D5 с временными описаниями и изображениями.

Шаг пользователя хранится в таблице d5. Нулевой шаг показывает вступление
с кнопкой «Поехали». Точки 1 и 2 предлагают загрузить фотографию;
точка 3 содержит поздравление с завершением.
"""

from .base import DiameterRoute, RoutePoint
from .placeholders import IMAGE_PLACEHOLDER


class D5Route(DiameterRoute):
    """Отвечает на выбор D5, используя прогресс из таблицы d5.

    introduction содержит пояснение и спойлеры нулевой точки. Каждая
    точка имеет отдельные text и image для будущего наполнения маршрута.
    Последний элемент points является финальным.
    """

    diameter = "d5"
    introduction = RoutePoint(
        text=(
            "D5: знакомство с маршрутом.\n\n"
            "Здесь будет пояснение к маршруту.\n\n"
            "Спойлеры: здесь будет обзор предстоящих точек."
        ),
        image=IMAGE_PLACEHOLDER,
    )
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
