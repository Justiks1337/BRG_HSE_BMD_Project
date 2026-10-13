import asyncio
import logging
import os

from aiogram import Dispatcher

from telegram import Bot
from telegram.handlers import router


async def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Задайте переменную окружения BOT_TOKEN")

    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    bot = Bot(token=token)
    await dispatcher.start_polling(bot.aiogram_bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
