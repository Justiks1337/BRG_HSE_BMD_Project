from ..proxy import MessageProxy, ResponseBuilder, ResponseProxy
from .command import Command


class GalleryComand(Command):
    """Базовый обработчик команды /gallery."""

    async def execute(self, message: MessageProxy) -> ResponseProxy:
        return ResponseBuilder().with_text("Команда /gallery получена.").build()
