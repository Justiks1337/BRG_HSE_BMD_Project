"""Выбирает обработчики команд и нажатий кнопок в личном чате.

Telegram-события поступают в роутеры как Proxy. Результат работы команд
и маршрутов возвращается в Telegram-слой в виде ResponseProxy.
"""

from ..proxy import CallbackQueryProxy, MessageProxy, ResponseProxy
from .bingo import BingoRoute
from .commands import RoadmapCommand, StartCommand, SupportCommand
from .diameters import D1Route, D2Route, D3Route, D4Route, D5Route


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
    """Передаёт выбор маршрута или бинго соответствующему обработчику.

    D1–D5 показывают сохранённый шаг пользователя, а бинго — таблицу
    заданий с отметками о выполнении.
    Значения upload:d1–upload:d5 зарезервированы для загрузки фотографии
    и не используются для выбора точки маршрута.
    """

    async def route(self, callback: CallbackQueryProxy) -> ResponseProxy | None:
        """Выбирает обработчик маршрута или бинго по полному callback_data.

        Args:
            callback: Данные нажатия кнопки, подготовленные Mapper.

        Returns:
            Текущая точка маршрута или карточка бинго. Для неизвестных
            кнопок и любых callback вне личного чата возвращается None.
        """
        # Признак личного чата вычисляется Mapper; core не зависит от aiogram.
        if not callback.is_private:
            return None

        match callback.data:
            case "roadmap:d1":
                route = D1Route()
            case "roadmap:d2":
                route = D2Route()
            case "roadmap:d3":
                route = D3Route()
            case "roadmap:d4":
                route = D4Route()
            case "roadmap:d5":
                route = D5Route()
            case "roadmap:bingo":
                route = BingoRoute()
            case _:
                return None

        return await route.execute(callback)
