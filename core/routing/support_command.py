from ..proxy import MessageProxy, ResponseBuilder, ResponseProxy
from .command import Command
from .texts import SUPPORT_TEXT

class SupportCommand(Command):
    """Базовый обработчик команды /support."""

    async def execute(self, message: MessageProxy) -> ResponseProxy:
        return ResponseBuilder().with_text(SUPPORT_TEXT).build()
