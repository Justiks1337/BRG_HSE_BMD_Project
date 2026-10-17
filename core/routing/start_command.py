from ..proxy import MessageProxy, ResponseBuilder, ResponseProxy
from .command import Command
from ..utils.DatabaseConnection import DatabaseConnection
from .texts import START_TEXT


class StartCommand(Command):
    """Базовый обработчик команды /start."""

    async def execute(self, message: MessageProxy) -> ResponseProxy:

        conn = DatabaseConnection()
        if not message.user_id:
            raise ValueError("message.user_id is None")

        # При вводе команды /start добавляем пользователя в базу данных
        await conn.add_user(message.user_id)
        return ResponseBuilder().with_text(START_TEXT).build()
