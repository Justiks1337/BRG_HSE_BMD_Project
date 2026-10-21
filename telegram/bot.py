"""Обёртка aiogram с HTML-форматированием и необязательным SOCKS-прокси.

Настройка применяется к текстам и подписям к медиа, включая ответы
на нажатия кнопок. При заданном URL сессия использует aiohttp-socks;
без URL запросы идут напрямую. Core остаётся независимым от aiogram.
"""

from typing import Any

from aiogram import Bot as AiogramBot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode


class Bot:
    """Хранит aiogram.Bot и проксирует обращения к его интерфейсу.

    Сообщения и подписи к изображениям интерпретируются как HTML.
    Предпросмотр ссылок отключён по умолчанию. При заданном proxy_url
    все запросы к Telegram выполняются через SOCKS-прокси.
    При прямом вызове метода Telegram API режим можно переопределить,
    например передать parse_mode=None для обычного текста.
    """

    def __init__(self, token: str, proxy_url: str | None = None) -> None:
        """Создаёт бота с общими настройками сообщений и HTTP-сессии.

        Args:
            token: Токен Telegram-бота, полученный у BotFather.
            proxy_url: SOCKS URL вида socks5://user:password@host:port
                или socks4://host:port. None, пустая строка и пробелы
                отключают прокси. Авторизация в URL необязательна.
        """
        proxy_url = (proxy_url or "").strip() or None
        session = AiohttpSession(proxy=proxy_url)
        self.aiogram_bot = AiogramBot(
            token=token,
            session=session,
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
