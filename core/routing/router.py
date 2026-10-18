"""Выбирает обработчики команд и нажатий кнопок в личном чате.

Telegram-события поступают в роутеры как Proxy. Результат работы команд
и маршрутов возвращается в Telegram-слой в виде ResponseProxy.
"""

from ..proxy import CallbackQueryProxy, MessageProxy, ResponseProxy
from .bingo import BingoPhotoHandler, BingoRoute, BingoTaskRoute, BingoUploadRoute
from .bingo.content import BINGO_TASKS
from .commands import RoadmapCommand, StartCommand, SupportCommand
from .diameters import D1Route, D2Route, D3Route, D4Route, D5Route


# Допускаем только канонические номера: без знака, пробелов и ведущих нулей.
_BINGO_TASK_NUMBERS = frozenset(str(number) for number in range(1, len(BINGO_TASKS) + 1))


class MessageRouter:
    """Направляет фотографии в бинго, а текст — обработчикам команд.

    Для выбора команды используется только её имя. Исходное сообщение
    вместе с аргументами передаётся в execute. Имена сравниваются целиком
    и с учётом регистра. Неизвестные команды возвращают None.
    """

    async def route(self, message: MessageProxy) -> ResponseProxy | None:
        """Обрабатывает загрузку фотографии либо выбирает команду по имени.

        Args:
            message: Исходное сообщение, подготовленное Mapper.

        Returns:
            Подтверждение загрузки или ответ команды. Возвращает None
            для неизвестного ввода, фотографии без ожидающего задания
            и любых сообщений вне личного чата.
        """
        # Команды доступны только в личном чате. Mapper определяет
        # этот признак по типу чата; core не зависит от aiogram.
        if not message.is_private:
            return None

        # Фотография связывается только с заранее выбранным заданием.
        # Проверяем её до текста: у фотографии текст сообщения отсутствует.
        if message.photo_file_id is not None:
            return await BingoPhotoHandler().execute(message)

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
    """Выбирает маршрут, задание бинго или запрос загрузки фотографии.

    D1–D5 показывают сохранённый шаг пользователя, а бинго — таблицу
    заданий с отметками о выполнении. bingo:N открывает задание,
    upload:bingo:N ожидает фотографию для него; N принимает значения 1–12.
    Значения upload:d1–upload:d5 зарезервированы для загрузки фотографии
    и не используются для выбора точки маршрута.
    """

    async def route(self, callback: CallbackQueryProxy) -> ResponseProxy | None:
        """Разбирает callback_data и передаёт проверенный номер обработчику.

        Args:
            callback: Данные нажатия кнопки, подготовленные Mapper.

        Returns:
            Карточка маршрута, бинго, задания либо просьба загрузить фото.
            Для неизвестных или некорректных callback_data и нажатий
            вне личного чата возвращается None.
        """
        # Признак личного чата вычисляется Mapper; core не зависит от aiogram.
        if not callback.is_private or not isinstance(callback.data, str):
            return None

        match callback.data.split(":"):
            case ["roadmap", "d1"]:
                route = D1Route()
            case ["roadmap", "d2"]:
                route = D2Route()
            case ["roadmap", "d3"]:
                route = D3Route()
            case ["roadmap", "d4"]:
                route = D4Route()
            case ["roadmap", "d5"]:
                route = D5Route()
            case ["roadmap", "bingo"]:
                route = BingoRoute()
            case ["bingo", number] if number in _BINGO_TASK_NUMBERS:
                return await BingoTaskRoute().execute(callback, int(number))
            case ["upload", "bingo", number] if number in _BINGO_TASK_NUMBERS:
                return await BingoUploadRoute().execute(callback, int(number))
            case _:
                return None

        return await route.execute(callback)
