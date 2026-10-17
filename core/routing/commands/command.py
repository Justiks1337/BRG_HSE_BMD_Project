from abc import ABC, abstractmethod

from ...proxy import MessageProxy, ResponseProxy


class Command(ABC):
    """Общий интерфейс команд бизнес-логики."""

    @abstractmethod
    async def execute(self, message: MessageProxy) -> ResponseProxy:
        """Обрабатывает данные сообщения и возвращает ответ пользователю."""
        ...
