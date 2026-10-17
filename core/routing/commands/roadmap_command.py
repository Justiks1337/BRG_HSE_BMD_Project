from ...proxy import ButtonProxy, MessageProxy, ResponseBuilder, ResponseProxy
from .command import Command


class RoadmapCommand(Command):
    """Готовит меню выбора ветки маршрута для команды /roadmap.

    Меню содержит D1–D5 и «Бинго», расположенные в две строки.
    Все кнопки изначально неактивны. Их идентификаторы сохранены
    в Proxy для будущего подключения обработчиков в ButtonRouter.
    Отправку сообщения выполняет Telegram-слой.
    """

    async def execute(self, message: MessageProxy) -> ResponseProxy:
        """Собирает текст меню и шесть неактивных кнопок.

        Args:
            message: Исходное сообщение с данными пользователя и чата.
                Принимается по общему интерфейсу Command; текущее меню
                одинаково для всех пользователей.

        Returns:
            Ответ для отправки пользователю через Telegram-хендлер.
        """
        # disabled управляет доступностью кнопки в Telegram.
        # Запуск действий по её идентификатору отдельно контролирует core.
        return (
            ResponseBuilder()
            .with_text("Ветки маршрута:\n\nВсе маршруты пока недоступны.")
            .add_button_row(
                ButtonProxy("D1", "roadmap:d1", disabled=True),
                ButtonProxy("D2", "roadmap:d2", disabled=True),
                ButtonProxy("D3", "roadmap:d3", disabled=True),
            )
            .add_button_row(
                ButtonProxy("D4", "roadmap:d4", disabled=True),
                ButtonProxy("D5", "roadmap:d5", disabled=True),
                ButtonProxy("Бинго", "roadmap:bingo", disabled=True),
            )
            .build()
        )
