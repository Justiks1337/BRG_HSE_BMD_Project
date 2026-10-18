"""Формирует карточку бинго с клавиатурой по выполненным заданиям.

Данные прогресса загружаются один раз в execute и остаются доступны
отдельно от клавиатуры для будущего формирования изображения.
"""

from io import BytesIO

from ...proxy import ButtonProxy, CallbackQueryProxy, ResponseBuilder, ResponseProxy
from ...utils.DatabaseConnection import DatabaseConnection
from .content import BINGO_IMAGE, BINGO_TASKS, BINGO_TEXT


class BingoRoute:
    """Отвечает на выбор «Бинго» карточкой с таблицей кнопок 3×4.

    Текст и картинка постоянны. Выполненные задания отмечаются символом
    ✅ перед номером клетки; остальные кнопки содержат только номер.
    Просмотр карточки не изменяет состояние заданий в БД.
    """

    async def execute(self, callback: CallbackQueryProxy) -> ResponseProxy:
        """Готовит карточку бинго для пользователя, нажавшего кнопку.

        Args:
            callback: Данные выбора бинго с идентификатором пользователя.

        Returns:
            Постоянные текст и картинка с тремя строками по четыре кнопки.
            Каждая кнопка содержит callback вида bingo:1–bingo:12.
        """
        completed_tasks = await DatabaseConnection().get_completed_bingo_tasks(
            callback.user_id
        )
        # Данные получены отдельно от построения кнопок. Этот же набор
        # completed_tasks можно передать будущему генератору картинки.
        builder = (
            ResponseBuilder()
            .with_text(BINGO_TEXT)
            .with_image(BytesIO(BINGO_IMAGE))
        )
        for start in range(0, len(BINGO_TASKS), 4):
            buttons = []
            for number in range(start + 1, min(start + 5, len(BINGO_TASKS) + 1)):
                text = f"✅ {number}" if number in completed_tasks else str(number)
                buttons.append(ButtonProxy(text, f"bingo:{number}"))
            builder.add_button_row(*buttons)
        return builder.build()
