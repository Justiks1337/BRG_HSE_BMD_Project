"""Завершает ожидающее задание бинго после получения фотографии.

Обработчик получает только MessageProxy: типы aiogram и скачивание файлов
ему не нужны. Для выполнения достаточно факта отправки фотографии.
После сохранения результата возвращается обновлённая карточка бинго.
"""

from ...proxy import MessageProxy, ResponseProxy
from ...utils.DatabaseConnection import DatabaseConnection
from .bingo_route import BingoRoute


class BingoPhotoHandler:
    """Отмечает в БД задание, для которого пользователь запросил загрузку.

    Фотографии без предварительного выбора задания не меняют прогресс.
    После успешной записи ожидание сбрасывается, поэтому следующая
    фотография не выполняет ещё одно задание автоматически.
    """

    async def execute(self, message: MessageProxy) -> ResponseProxy | None:
        """Сохраняет выполнение и возвращает обновлённую карточку бинго.

        Args:
            message: Сообщение из личного чата с данными фотографии.

        Returns:
            Карточка с актуальными галочками на изображении и кнопках
            либо None, если нет фотографии,
            отправителя или ожидающего невыполненного задания.
        """
        if message.user_id is None or message.photo_file_id is None:
            return None
        task_number = await DatabaseConnection().complete_bingo_upload(message.user_id)
        if task_number is None:
            return None
        # Выполнение уже сохранено и ожидание снято. Карточка читает
        # актуальный прогресс из БД после завершения этой записи.
        return await BingoRoute().build_response(message.user_id)
