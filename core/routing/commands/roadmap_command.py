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
    Перед названиями D1–D5 отображаются индивидуальные custom emoji.
    Кнопка D5 открывает текущую точку маршрута через ButtonRouter,
    а «Бинго» — карточку заданий. Кнопки D1–D4 помечены как «скоро»;
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
                ButtonProxy(
                    "D1 — скоро", "roadmap:d1", disabled=True,
                    icon_custom_emoji_id="5380022798297105587",
                ),
                ButtonProxy(
                    "D2 — скоро", "roadmap:d2", disabled=True,
                    icon_custom_emoji_id="5379938110131965042",
                ),
                ButtonProxy(
                    "D3 — скоро", "roadmap:d3", disabled=True,
                    icon_custom_emoji_id="5379926792893140809",
                ),
            )
            .add_button_row(
                ButtonProxy(
                    "D4 — скоро", "roadmap:d4", disabled=True,
                    icon_custom_emoji_id="5379619225990107477",
                ),
                ButtonProxy(
                    "D5", "roadmap:d5",
                    icon_custom_emoji_id="5379780338803313901",
                ),
                ButtonProxy("Бинго", "roadmap:bingo"),
            )
            .build()
        )
