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
        text: Вступление, описание точки либо поздравление с завершением.
        image: Байты изображения для этой точки, например из AssetsManager.
            При сборке ответа для них создаётся отдельный BytesIO.
    """

    text: str
    image: bytes


class DiameterRoute:
    """Формирует ответ для текущего шага конкретного диаметра.

    Подкласс задаёт diameter, introduction и упорядоченный кортеж points.
    Шаг 0 показывает вступление с кнопкой «Поехали». Точки с фотографиями
    начинаются с 1. Последний элемент points обозначает завершение;
    шаги за его пределами также показывают финальную точку.

    Attributes:
        diameter: Имя таблицы прогресса: d1, d2, d3, d4 или d5.
        introduction: Нулевая точка с пояснением и спойлерами маршрута.
        points: Точки маршрута, последняя из которых содержит поздравление.
    """

    diameter: str
    introduction: RoutePoint
    points: tuple[RoutePoint, ...]

    async def execute(self, callback: CallbackQueryProxy) -> ResponseProxy:
        """Готовит текущую точку по шагу пользователя в БД.

        Args:
            callback: Данные нажатия на кнопку выбора диаметра.

        Returns:
            Текст и изображение текущей точки. На шаге 0 доступна кнопка
            «Поехали» с callback_data вида route:start:d5. На обычных точках
            доступна «Загрузить фотографию» с callback_data вида upload:d5:1.
            Финальное поздравление отправляется без кнопок.
        """
        step = await DatabaseConnection().get_diameter_step(
            self.diameter, callback.user_id
        )
        return self.build_response(step)

    async def start(self, callback: CallbackQueryProxy) -> ResponseProxy:
        """Запускает маршрут из вступления и возвращает актуальную точку.

        Args:
            callback: Нажатие «Поехали» в личном чате пользователя.

        Returns:
            Первая точка для нового маршрута. Повторное нажатие старой
            кнопки возвращает текущую точку, не сбрасывая прогресс.
        """
        await DatabaseConnection().start_diameter(self.diameter, callback.user_id)
        return await self.execute(callback)

    def build_response(self, step: int) -> ResponseProxy:
        """Собирает карточку точки по известному шагу без обращения к БД.

        Используется при выборе маршрута, его запуске и после фотографии.
        Последний элемент points содержит поздравление без кнопок.

        Args:
            step: Номер шага: 0 для вступления, от 1 для точек маршрута.

        Returns:
            Вступление с «Поехали», точка с загрузкой либо поздравление.

        Raises:
            ValueError: Если шаг не является неотрицательным целым числом.
        """
        if type(step) is not int or step < 0:
            raise ValueError("Шаг маршрута должен быть неотрицательным целым числом")
        point = (
            self.introduction if step == 0
            else self.points[min(step, len(self.points)) - 1]
        )
        builder = (
            ResponseBuilder()
            .with_text(point.text)
            .with_image(BytesIO(point.image))
        )
        # Вступление запускается кнопкой; обычная точка завершается фото.
        # Сам просмотр карточки не меняет прогресс пользователя.
        if step == 0:
            builder.add_button_row(ButtonProxy("Поехали", f"route:start:{self.diameter}"))
        elif step < len(self.points):
            # Номер шага защищает от повторного использования старой кнопки.
            # В core формируется строка, без зависимости от aiogram.
            builder.add_button_row(
                ButtonProxy("Загрузить фотографию", f"upload:{self.diameter}:{step}")
            )
        return builder.build()
