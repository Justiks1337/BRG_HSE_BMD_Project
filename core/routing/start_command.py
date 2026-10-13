from ..proxy import MessageProxy, ResponseBuilder, ResponseProxy
from .command import Command


class StartCommand(Command):
    """Базовый обработчик команды /start."""

    async def execute(self, message: MessageProxy) -> ResponseProxy:
        return ResponseBuilder().with_text("Команда /start получена.").build()
