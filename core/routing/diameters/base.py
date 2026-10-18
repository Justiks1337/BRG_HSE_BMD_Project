"""Модель точки маршрута и общая логика ответа по сохранённому шагу.

Модуль работает с данными core и БД. Отправку изображения и преобразование
кнопок в объекты aiogram выполняет Telegram-слой.
"""

from dataclasses import dataclass
from io import BytesIO

from ...proxy import ButtonProxy, CallbackQueryProxy, ResponseBuilder, ResponseProxy
from ...utils.DatabaseConnection import DatabaseConnection


@dataclass(frozen=True, slots=True)
class RoutePoint:
    """Хранит содержимое одной точки маршрута.

    Attributes:
        text: Описание точки либо поздравление с завершением маршрута.
        image: Содержимое изображения. Для каждой точки его можно заменить
            независимо от остальных; сейчас используется PNG-заглушка.
    """

    text: str
    image: bytes


class DiameterRoute:
    """Формирует ответ для текущего шага конкретного диаметра.

    Подкласс задаёт diameter и упорядоченный кортеж points. Шаги в БД
    начинаются с 1. Последний элемент points всегда обозначает завершение
    маршрута; шаги за его пределами также показывают финальную точку.

    Attributes:
        diameter: Имя таблицы прогресса: d1, d2, d3, d4 или d5.
        points: Точки маршрута, последняя из которых содержит поздравление.
    """

    diameter: str
    points: tuple[RoutePoint, ...]

    async def execute(self, callback: CallbackQueryProxy) -> ResponseProxy:
        """Готовит текущую точку по шагу пользователя в БД.

        Args:
            callback: Данные нажатия на кнопку выбора диаметра.

        Returns:
            Текст и изображение точки. До финала ответ содержит кнопку
            «Загрузить фотографию» с callback_data вида upload:d1–upload:d5.
            Финальное поздравление отправляется без кнопок.
        """
        step = await DatabaseConnection().get_diameter_step(
            self.diameter, callback.user_id
        )
        index = min(step, len(self.points)) - 1
        point = self.points[index]
        builder = (
            ResponseBuilder()
            .with_text(point.text)
            .with_image(BytesIO(point.image))
        )
        # Просмотр точки не меняет step. Переход будет выполняться
        # обработчиком загрузки фотографии, а не нажатием на диаметр.
        if index < len(self.points) - 1:
            # Схема prefix:diameter совместима с форматом CallbackData.
            # В core формируется строка, без зависимости от aiogram.
            builder.add_button_row(
                ButtonProxy("Загрузить фотографию", f"upload:{self.diameter}")
            )
        return builder.build()
