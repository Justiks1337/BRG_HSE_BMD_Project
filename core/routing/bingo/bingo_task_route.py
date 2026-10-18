"""Показывает описание выбранного задания бинго и доступное действие.

Номер задания приходит из роутера после проверки callback_data. Прогресс
читается заново при каждом нажатии, включая нажатия старых кнопок.
"""

from io import BytesIO

from ...proxy import ButtonProxy, CallbackQueryProxy, ResponseBuilder, ResponseProxy
from ...utils.DatabaseConnection import DatabaseConnection
from .content import BINGO_TASK_IMAGE, BINGO_TASKS


class BingoTaskRoute:
    """Формирует карточку задания с изображением и состоянием выполнения.

    Описание и картинка одинаковы до и после выполнения. Выполненная
    карточка получает отметку, а невыполненная — кнопку загрузки фотографии.
    """

    async def execute(
        self, callback: CallbackQueryProxy, task_number: int,
    ) -> ResponseProxy:
        """Возвращает карточку задания с номером от 1 до 12.

        Args:
            callback: Данные пользователя, открывшего задание.
            task_number: Проверенный роутером номер клетки бинго.

        Returns:
            Ответ с картинкой, описанием и кнопкой либо отметкой выполнения.

        Raises:
            ValueError: Если номер задания выходит за границы списка.
        """
        if not 1 <= task_number <= len(BINGO_TASKS):
            raise ValueError("Неизвестное задание бинго")
        completed_tasks = await DatabaseConnection().get_completed_bingo_tasks(
            callback.user_id
        )
        completed = task_number in completed_tasks
        text = BINGO_TASKS[task_number - 1]
        if completed:
            text += "\n\nВыполнено ✅"
        builder = (
            ResponseBuilder()
            .with_text(text)
            .with_image(BytesIO(BINGO_TASK_IMAGE))
        )
        if not completed:
            builder.add_button_row(
                ButtonProxy("Загрузить фотографию", f"upload:bingo:{task_number}")
            )
        return builder.build()
