"""Отсекает частые действия до роутеров core, запросов к БД и сборки картинок.

Один экземпляр подключается к сообщениям и callback query, чтобы команды,
кнопки и фотографии использовали общий лимит пользователя.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import CallbackQuery, Message, TelegramObject

from core.utils.rate_limiter import RateLimiter


class RateLimitMiddleware(BaseMiddleware):
    """Применяет общий лимит к командам, фотографиям и нажатиям кнопок.

    Команды с префиксом / и фотографии проверяются в личном чате.
    Все callback проверяются до подтверждения нажатия, включая события
    без доступного сообщения. Это ограничивает и исходящие запросы API.
    Остальные сообщения проходят обычную маршрутизацию. Превышение
    игнорируется без ответа, чтобы спам не порождал поток исходящих запросов.
    """

    def __init__(self, limiter: RateLimiter) -> None:
        """Принимает общее хранилище лимитов для сообщений и нажатий кнопок.

        Args:
            limiter: Независимый от aiogram ограничитель с настройками
                количества действий, длины окна и размера истории.
        """
        self._limiter = limiter

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Передаёт допустимое событие обработчику либо останавливает его.

        Args:
            handler: Следующий обработчик middleware-цепочки aiogram.
            event: Сообщение или нажатие кнопки Telegram.
            data: Контекст текущего обновления, передаваемый без изменений.

        Returns:
            Результат следующего обработчика или None при превышении лимита.
            Проверка выполняется до Mapper и бизнес-логики. Неподдерживаемые
            события и события без отправителя передаются обычному обработчику.
        """
        if isinstance(event, Message):
            protected = event.chat.type == ChatType.PRIVATE and (
                bool(event.photo)
                or bool(event.text and event.text.lstrip().startswith("/"))
            )
        elif isinstance(event, CallbackQuery):
            protected = True
        else:
            return await handler(event, data)
        user = event.from_user
        if protected and user is not None and not self._limiter.allow(user.id):
            return None
        return await handler(event, data)
