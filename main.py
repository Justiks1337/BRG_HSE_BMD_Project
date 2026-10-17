import asyncio
import logging
import os

from aiogram import Dispatcher
from dotenv import load_dotenv

from core.utils.DatabaseConnection import DatabaseConnection
from telegram import Bot
from telegram.handlers import router

async def main() -> None:
    """Настраивает приложение и принимает обновления через long polling.

    BOT_TOKEN и DATABASE_NAME задаются через окружение или .env.
    Соединение с БД открывается до приёма сообщений: команда /start
    использует его для регистрации пользователя. При завершении
    polling или ошибке соединение закрывается в finally.

    Raises:
        RuntimeError: Если переменная BOT_TOKEN не задана.
    """
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Задайте переменную окружения BOT_TOKEN")

    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    database = DatabaseConnection()
    try:
        await database.get_connection()
        bot = Bot(token=token)
        await dispatcher.start_polling(bot.aiogram_bot)
    finally:
        # Закрываем БД и при ошибке подготовки таблиц или запуска бота.
        await database.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
