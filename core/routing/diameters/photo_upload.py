"""Запрос фотографии для точки D1–D5 и переход к следующей точке.

Ожидание хранится в БД вместе с номером показанного шага. Само изображение
не скачивается: для прохождения достаточно входящего MessageProxy с фото.
"""

from ...proxy import CallbackQueryProxy, MessageProxy, ResponseBuilder, ResponseProxy
from ...utils.DatabaseConnection import DatabaseConnection
from .base import DiameterRoute
from .d1 import D1Route
from .d2 import D2Route
from .d3 import D3Route
from .d4 import D4Route
from .d5 import D5Route


# Один перечень обработчиков для кнопок загрузки и ответа после фотографии.
DIAMETER_ROUTES: dict[str, type[DiameterRoute]] = {
    "d1": D1Route,
    "d2": D2Route,
    "d3": D3Route,
    "d4": D4Route,
    "d5": D5Route,
}


class DiameterUploadRoute:
    """Ожидает фотографию для выбранной точки, не меняя прогресс маршрута.

    Последний запрос загрузки заменяет предыдущий, в том числе из бинго.
    Старая кнопка не создаёт ожидание для уже пройденной точки.
    """

    async def execute(
        self, callback: CallbackQueryProxy, diameter: str, step: int,
    ) -> ResponseProxy:
        """Запрашивает фото для актуального шага либо показывает текущую точку.

        Args:
            callback: Пользователь, нажавший кнопку в личном чате.
            diameter: Проверенное роутером имя диаметра d1–d5.
            step: Номер точки из проверенного callback_data.

        Returns:
            Просьба отправить фото либо текущая карточка для старой кнопки.
        """
        route = DIAMETER_ROUTES[diameter]()
        requested = await DatabaseConnection().request_diameter_upload(
            callback.user_id, diameter, step, len(route.points)
        )
        if not requested:
            return await route.execute(callback)
        return (
            ResponseBuilder()
            .with_text(f"Пришлите фотографию для точки {step} маршрута {diameter.upper()}.")
            .build()
        )


class DiameterPhotoHandler:
    """Сохраняет прохождение точки и показывает следующий шаг маршрута.

    Без ожидающей загрузки фотография не меняет прогресс. После последней
    обычной точки отправляется поздравление с картинкой и без кнопок.
    """

    async def execute(self, message: MessageProxy) -> ResponseProxy | None:
        """Обрабатывает фотографию только для предварительно выбранной точки.

        Args:
            message: Сообщение из личного чата с идентификатором фотографии.

        Returns:
            Следующая точка или поздравление; None, если нет фотографии,
            отправителя либо актуального ожидания для маршрута.
        """
        if message.user_id is None or message.photo_file_id is None:
            return None
        completed = await DatabaseConnection().complete_diameter_upload(message.user_id)
        if completed is None:
            return None
        diameter, next_step = completed
        return DIAMETER_ROUTES[diameter]().build_response(next_step)
