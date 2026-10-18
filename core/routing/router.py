"""Выбирает обработчики команд и нажатий кнопок в личном чате.

Telegram-события поступают в роутеры как Proxy. Результат работы команд
и маршрутов возвращается в Telegram-слой в виде ResponseProxy.
"""

from ..proxy import CallbackQueryProxy, MessageProxy, ResponseProxy
from .bingo import BingoPhotoHandler, BingoRoute, BingoTaskRoute, BingoUploadRoute
from .bingo.content import BINGO_TASKS
from .commands import RoadmapCommand, StartCommand, SupportCommand
from .diameters import (
    DIAMETER_ROUTES,
    D1Route, D2Route, D3Route, D4Route, D5Route,
    DiameterPhotoHandler,
    DiameterUploadRoute,
)


# Допускаем только канонические номера: без знака, пробелов и ведущих нулей.
_BINGO_TASK_NUMBERS = frozenset(str(number) for number in range(1, len(BINGO_TASKS) + 1))

_DIAMETER_STEP_NUMBERS = {
    diameter: frozenset(str(step) for step in range(1, len(route.points)))
    for diameter, route in DIAMETER_ROUTES.items()
}


class MessageRouter:
    """Направляет фотографии в маршруты или бинго, а текст — командам.

    Для выбора команды используется только её имя. Исходное сообщение
    вместе с аргументами передаётся в execute. Имена сравниваются целиком
    и с учётом регистра. Неизвестные команды возвращают None.
    """

    async def route(self, message: MessageProxy) -> ResponseProxy | None:
        """Обрабатывает загрузку фотографии либо выбирает команду по имени.

        Args:
            message: Исходное сообщение, подготовленное Mapper.

        Returns:
            Следующая точка маршрута, подтверждение бинго или ответ команды.
            Возвращает None
            для неизвестного ввода, фотографии без ожидающей загрузки
            и любых сообщений вне личного чата.
        """
        # Команды доступны только в личном чате. Mapper определяет
        # этот признак по типу чата; core не зависит от aiogram.
        if not message.is_private:
            return None

        # Общее ожидание в БД связывает фото с одной точкой или заданием.
        # Проверяем её до текста: у фотографии текст сообщения отсутствует.
        if message.photo_file_id is not None:
            response = await DiameterPhotoHandler().execute(message)
            if response is not None:
                return response
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
    upload:d5:1 ожидает фотографию для первой точки D5. Номер шага
    проверяется по списку точек, а его актуальность — по прогрессу в БД.
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
            case ["upload", diameter, step] if (
                diameter in _DIAMETER_STEP_NUMBERS
                and step in _DIAMETER_STEP_NUMBERS[diameter]
            ):
                return await DiameterUploadRoute().execute(callback, diameter, int(step))
            case _:
                return None

        return await route.execute(callback)
