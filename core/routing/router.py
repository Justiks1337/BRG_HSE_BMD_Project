from ..proxy import MessageProxy, ResponseProxy
from .bingo_command import BingoCommand
from .gallery_comand import GalleryComand
from .start_command import StartCommand
from .support_command import SupportCommand


class MessageRouter:
    """Выбирает команду по первому слову сообщения.

    Для выбора команды используется только её имя. Исходное сообщение
    вместе с аргументами передаётся в execute. Имена сравниваются целиком
    и с учётом регистра. Неизвестные команды возвращают None.
    """

    async def route(self, message: MessageProxy) -> ResponseProxy | None:
        """Отделяет команду от аргументов и вызывает её execute.

        Сообщения без текста, пустой ввод и обычный текст возвращают None.
        """
        if not isinstance(message.text, str):
            return None

        parts = message.text.split(maxsplit=1)
        if not parts:
            return None

        match parts[0]:
            case "/start":
                command = StartCommand()
            case "/bingo":
                command = BingoCommand()
            case "/support":
                command = SupportCommand()
            case "/gallery":
                command = GalleryComand()
            case _:
                return None

        return await command.execute(message)


class ButtonRouter:
    pass
