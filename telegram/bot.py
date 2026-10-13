from typing import Any

from aiogram import Bot as AiogramBot


class Bot:
    """Обёртка над aiogram.Bot на основе композиции."""

    def __init__(self, token: str) -> None:
        self.aiogram_bot = AiogramBot(token=token)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.aiogram_bot, name)

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Проксирует вызовы bot(TelegramMethod(...))."""
        return await self.aiogram_bot(*args, **kwargs)
