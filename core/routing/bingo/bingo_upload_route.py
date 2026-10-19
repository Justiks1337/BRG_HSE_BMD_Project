"""Связывает следующую фотографию пользователя с выбранным заданием бинго."""

from ...proxy import CallbackQueryProxy, ResponseBuilder, ResponseProxy
from ...utils.DatabaseConnection import DatabaseConnection
from .bingo_task_route import BingoTaskRoute


class BingoUploadRoute:
    """Запоминает задание для загрузки, не отмечая его выполненным.

    Один пользователь может ожидать одну фотографию для бинго или маршрута.
    Новый выбор заменяет предыдущий и сбрасывается при перезапуске бота.
    """

    async def execute(
        self, callback: CallbackQueryProxy, task_number: int,
    ) -> ResponseProxy:
        """Запрашивает фотографию либо показывает уже выполненное задание.

        Args:
            callback: Данные пользователя, нажавшего кнопку загрузки.
            task_number: Номер задания из проверенного callback_data.

        Returns:
            Просьба отправить фотографию. Если старая кнопка относится
            к выполненному заданию, возвращает его карточку без кнопки.
        """
        requested = await DatabaseConnection().request_bingo_upload(
            callback.user_id, task_number
        )
        if not requested:
            return await BingoTaskRoute().execute(callback, task_number)
        return (
            ResponseBuilder()
            .with_text(f"Пришлите фотографию для задания {task_number}.")
            .build()
        )
