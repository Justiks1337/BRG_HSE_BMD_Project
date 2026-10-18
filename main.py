"""Подготавливает ресурсы и БД перед запуском Telegram-бота.

Файлы ресурсов загружаются в память, а изображения ячеек бинго готовятся
в рабочем потоке до приёма обновлений. Ошибка прогрева останавливает
запуск до начала polling. Генераторы используют подготовленные ресурсы.
"""

import asyncio
import logging
import os

from aiogram import Dispatcher
from dotenv import load_dotenv

from core.utils.AssetsManager import AssetsManager
from core.utils.DatabaseConnection import DatabaseConnection
from telegram import Bot
from telegram.handlers import router


def _prepare_bingo_images() -> None:
    """Прогревает кеш бинго после загрузки файлов и до приёма обновлений.

    Выполняется в рабочем потоке. Локальный импорт откладывает чтение
    ресурсов в полях класса до завершения AssetsManager.load_assets.
    Ошибки декодирования, шрифта и размещения текста передаются в main.
    """
    from core.routing.bingo.bingo_image_builder import BingoImageBuilder

    BingoImageBuilder.prepare_images()


async def main() -> None:
    """Настраивает приложение и принимает обновления через long polling.

    BOT_TOKEN и DATABASE_NAME задаются через окружение или .env.
    Ресурсы загружаются в память через asyncio.to_thread. Затем до начала
    polling подготавливаются все текстовые ячейки бинго и общая галочка.
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

    # Ресурсы должны быть готовы до первого импорта BingoImageBuilder:
    # изображения сохраняются в полях его класса.
    await asyncio.to_thread(AssetsManager().load_assets)
    # Ждём полного прогрева: первый пользователь получает готовые ячейки.
    await asyncio.to_thread(_prepare_bingo_images)

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
