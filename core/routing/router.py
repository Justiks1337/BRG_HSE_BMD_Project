from ..proxy import CallbackQueryProxy, MessageProxy, ResponseProxy
from .commands import RoadmapCommand, StartCommand, SupportCommand


class MessageRouter:
    """Выбирает команду по первому слову сообщения.

    Для выбора команды используется только её имя. Исходное сообщение
    вместе с аргументами передаётся в execute. Имена сравниваются целиком
    и с учётом регистра. Неизвестные команды возвращают None.
    """

    async def route(self, message: MessageProxy) -> ResponseProxy | None:
        """Отделяет команду от аргументов и вызывает её execute.

        Args:
            message: Исходное сообщение, подготовленное Mapper.

        Returns:
            Ответ выбранной команды либо None для пустого ввода,
            сообщений без текста, неизвестных команд и любых
            сообщений вне личного чата.
        """
        # Команды доступны только в личном чате. Mapper определяет
        # этот признак по типу чата; core не зависит от aiogram.
        if not message.is_private:
            return None

        if not isinstance(message.text, str):
            return None

        # Сравниваем полное имя: /roadmap arg подходит, /roadmap123 — нет.
        # Исходный текст сохраняется в message для самой команды.
        parts = message.text.split(maxsplit=1)
        if not parts:
            return None

        match parts[0]:
            case "/start":
                command = StartCommand()
            case "/roadmap":
                command = RoadmapCommand()
            case "/support":
                command = SupportCommand()
            case _:
                return None

        return await command.execute(message)


class ButtonRouter:
    """Распознаёт кнопки выбора ветки маршрута.

    Все шесть маршрутов пока отключены. Даже при получении callback
    из старого сообщения или вручную сформированного запроса
    действия по маршруту не выполняются.
    """

    async def route(self, callback: CallbackQueryProxy) -> ResponseProxy | None:
        """Распознаёт идентификатор кнопки без запуска маршрута.

        Args:
            callback: Данные нажатия, подготовленные Mapper. Поле data
                рассматривается как пользовательский ввод.

        Returns:
            Пока None для всех кнопок: маршруты отключены. Неизвестные
            идентификаторы также игнорируются. Подтверждение callback
            выполняет Telegram-хендлер. Callback вне личного чата
            игнорируются до выбора обработчика.
        """
        # Обрабатываем кнопки только из личного чата. Если исходного
        # сообщения нет, Mapper выставляет is_private=False.
        if not callback.is_private:
            return None

        # Проверяем полное значение; префикс roadmap: сам по себе
        # не даёт права на запуск какого-либо действия.
        match callback.data:
            case (
                "roadmap:d1"
                | "roadmap:d2"
                | "roadmap:d3"
                | "roadmap:d4"
                | "roadmap:d5"
                | "roadmap:bingo"
            ):
                # Здесь будут обработчики после включения маршрутов.
                return None
            case _:
                return None
