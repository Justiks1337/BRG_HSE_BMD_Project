"""Формирует меню диаметров D1–D5 с активной кнопкой D5.

Текст меню берётся из ROADMAP_TEXT, а обработчики его кнопок выбираются
в ButtonRouter по значениям roadmap:d1–roadmap:d5.
"""

from ...proxy import ButtonProxy, MessageProxy, ResponseBuilder, ResponseProxy
from .command import Command
from ..texts import ROADMAP_TEXT


class RoadmapCommand(Command):
    """Готовит меню выбора ветки маршрута для команды /roadmap.

    Меню содержит D1–D5 и «Бинго», расположенные в две строки.
    Кнопка D5 открывает текущую точку маршрута через ButtonRouter.
    Кнопки D1–D4 и «Бинго» пока неактивны. Обработчики D1–D4
    сохранены для последующего включения.
    Отправку сообщения выполняет Telegram-слой.
    """

    async def execute(self, message: MessageProxy) -> ResponseProxy:
        """Собирает меню с активной D5; D1–D4 и «Бинго» отключены.

        Args:
            message: Исходное сообщение с данными пользователя и чата.
                Принимается по общему интерфейсу Command; текущее меню
                одинаково для всех пользователей.

        Returns:
            Ответ для отправки пользователю через Telegram-хендлер.
        """
        # Выбор ветки использует префикс roadmap:. Кнопки загрузки
        # фотографии используют префикс upload: (например, upload:d5).
        return (
            ResponseBuilder()
            .with_text(ROADMAP_TEXT)
            .add_button_row(
                ButtonProxy("D1", "roadmap:d1", disabled=True),
                ButtonProxy("D2", "roadmap:d2", disabled=True),
                ButtonProxy("D3", "roadmap:d3", disabled=True),
            )
            .add_button_row(
                ButtonProxy("D4", "roadmap:d4", disabled=True),
                ButtonProxy("D5", "roadmap:d5"),
                ButtonProxy("Бинго", "roadmap:bingo", disabled=True),
            )
            .build()
        )
