"""Обёртка aiogram с HTML-форматированием исходящих сообщений по умолчанию.

Настройка применяется к текстам и подписям к медиа, включая ответы
на нажатия кнопок. Бизнес-логика core остаётся независимой от aiogram.
"""

from typing import Any

from aiogram import Bot as AiogramBot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


class Bot:
    """Хранит aiogram.Bot и проксирует обращения к его интерфейсу.

    Сообщения и подписи к изображениям интерпретируются как HTML.
    Предпросмотр ссылок отключён по умолчанию.
    При прямом вызове метода Telegram API режим можно переопределить,
    например передать parse_mode=None для обычного текста.
    """

    def __init__(self, token: str) -> None:
        """Создаёт бота с HTML-режимом и отключённым превью ссылок.

        Args:
            token: Токен Telegram-бота, полученный у BotFather.
        """
        self.aiogram_bot = AiogramBot(
            token=token,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
                link_preview_is_disabled=True,
            ),
        )

    def __getattr__(self, name: str) -> Any:
        """Возвращает атрибут или метод вложенного aiogram.Bot по имени.

        Args:
            name: Имя атрибута, отсутствующего у обёртки.

        Raises:
            AttributeError: Если вложенный бот также не имеет атрибута.
        """
        return getattr(self.aiogram_bot, name)

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Выполняет bot(TelegramMethod(...)) через вложенного бота.

        Передаёт аргументы без изменений. Если TelegramMethod использует
        режим форматирования по умолчанию, применяется HTML.
        """
        return await self.aiogram_bot(*args, **kwargs)
