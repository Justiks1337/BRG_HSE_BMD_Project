from ..proxy import MessageProxy, ResponseBuilder, ResponseProxy
from .command import Command


class BingoCommand(Command):
    """Базовый обработчик команды /bingo."""

    async def execute(self, message: MessageProxy) -> ResponseProxy:
        return ResponseBuilder().with_text("Команда /bingo получена.").build()
