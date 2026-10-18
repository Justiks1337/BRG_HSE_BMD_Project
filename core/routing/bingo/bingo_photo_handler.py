"""Завершает ожидающее задание бинго после получения фотографии.

Обработчик получает только MessageProxy: типы aiogram и скачивание файлов
ему не нужны. Для выполнения достаточно факта отправки фотографии.
"""

from ...proxy import MessageProxy, ResponseBuilder, ResponseProxy
from ...utils.DatabaseConnection import DatabaseConnection


class BingoPhotoHandler:
    """Отмечает в БД задание, для которого пользователь запросил загрузку.

    Фотографии без предварительного выбора задания не меняют прогресс.
    После успешной записи ожидание сбрасывается, поэтому следующая
    фотография не выполняет ещё одно задание автоматически.
    """

    async def execute(self, message: MessageProxy) -> ResponseProxy | None:
        """Сохраняет выполнение и возвращает подтверждение пользователю.

        Args:
            message: Сообщение из личного чата с данными фотографии.

        Returns:
            Подтверждение выполнения либо None, если нет фотографии,
            отправителя или ожидающего невыполненного задания.
        """
        if message.user_id is None or message.photo_file_id is None:
            return None
        task_number = await DatabaseConnection().complete_bingo_upload(message.user_id)
        if task_number is None:
            return None
        return (
            ResponseBuilder()
            .with_text(f"Задание {task_number} выполнено ✅.")
            .build()
        )
