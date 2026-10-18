"""Формирует меню диаметров D1–D5 с активными кнопками D5 и «Бинго».

Текст меню берётся из ROADMAP_TEXT, а обработчики его кнопок выбираются
в ButtonRouter по значениям roadmap:d1–roadmap:d5 и roadmap:bingo.
"""

from ...proxy import ButtonProxy, MessageProxy, ResponseBuilder, ResponseProxy
from .command import Command
from ..texts import ROADMAP_TEXT


class RoadmapCommand(Command):
    """Готовит меню выбора ветки маршрута для команды /roadmap.

    Меню содержит D1–D5 и «Бинго», расположенные в две строки.
    Кнопка D5 открывает текущую точку маршрута через ButtonRouter,
    а «Бинго» — карточку заданий. Кнопки D1–D4 пока неактивны;
    их обработчики сохранены для последующего включения.
    Отправку сообщения выполняет Telegram-слой.
    """

    async def execute(self, message: MessageProxy) -> ResponseProxy:
        """Собирает меню с активными D5 и «Бинго»; D1–D4 отключены.

        Args:
            message: Исходное сообщение с данными пользователя и чата.
                Принимается по общему интерфейсу Command; текущее меню
                одинаково для всех пользователей.

        Returns:
            Ответ для отправки пользователю через Telegram-хендлер.
        """
        # Выбор ветки использует префикс roadmap:. Кнопки загрузки
        # фотографии используют префикс upload: (например, upload:d5:1).
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
                ButtonProxy("Бинго", "roadmap:bingo"),
            )
            .build()
        )
