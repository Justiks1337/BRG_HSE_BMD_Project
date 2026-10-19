"""Формирует карточку бинго с клавиатурой по выполненным заданиям.

Данные прогресса загружаются один раз в build_response и используются для
картинки и клавиатуры. Pillow-сборка выполняется через asyncio.to_thread,
чтобы не блокировать обработку Telegram-событий в цикле asyncio.
"""

import asyncio
from io import BytesIO

from ...proxy import ButtonProxy, CallbackQueryProxy, ResponseBuilder, ResponseProxy
from ...utils.DatabaseConnection import DatabaseConnection
from .content import BINGO_TASKS, BINGO_TEXT


class BingoRoute:
    """Отвечает на выбор «Бинго» карточкой с таблицей кнопок 3×4.

    Текст карточки постоянен. На картинке выполненные задания заменяются
    галочками, остальные показывают заголовки заданий из BINGO_TASKS.
    На кнопках выполненные задания отмечаются символом ✅ перед номером.
    Просмотр карточки не изменяет состояние заданий в БД.
    """

    async def execute(self, callback: CallbackQueryProxy) -> ResponseProxy:
        """Готовит карточку бинго для пользователя, нажавшего кнопку.

        Args:
            callback: Данные выбора бинго с идентификатором пользователя.

        Returns:
            Текст, изображение прогресса и три строки по четыре кнопки.
            Каждая кнопка содержит callback вида bingo:1–bingo:12.
        """
        return await self.build_response(callback.user_id)

    async def build_response(self, user_id: int) -> ResponseProxy:
        """Формирует общую карточку для кнопки бинго и ответа на загрузку фото.

        Прогресс читается заново при каждом вызове. Одна выборка определяет
        галочки на изображении и кнопках, включая только что выполненное
        задание. Pillow-сборка выполняется в рабочем потоке.

        Args:
            user_id: Идентификатор пользователя, чей прогресс нужно показать.

        Returns:
            Текст бинго, изображение поля и клавиатура из двенадцати кнопок
            с актуальными отметками выполнения.
        """
        completed_tasks = await DatabaseConnection().get_completed_bingo_tasks(
            user_id
        )
        # Поток получает неизменяемый снимок тех же данных, что и клавиатура.
        # Создание Builder, рисование и кодирование PNG выполняются вне цикла событий.
        image = await asyncio.to_thread(self._build_image, frozenset(completed_tasks))
        builder = (
            ResponseBuilder()
            .with_text(BINGO_TEXT)
            .with_image(image)
        )
        for start in range(0, len(BINGO_TASKS), 4):
            buttons = []
            for number in range(start + 1, min(start + 5, len(BINGO_TASKS) + 1)):
                text = f"✅ {number}" if number in completed_tasks else str(number)
                buttons.append(ButtonProxy(text, f"bingo:{number}"))
            builder.add_button_row(*buttons)
        return builder.build()

    @staticmethod
    def _build_image(completed_tasks: frozenset[int]) -> BytesIO:
        """Строит изображение бинго целиком в рабочем потоке.

        Args:
            completed_tasks: Номера выполненных заданий из единой выборки БД.
                Каждая сборка создаёт собственный Builder и буфер результата.

        Returns:
            Новый PNG-буфер: галочки для выполненных клеток и заголовки
            из BINGO_TASKS для остальных. Нумерация начинается с 1.
        """
        # Builder уже подготовлен при запуске. Локальный импорт нужен,
        # чтобы импорт core до загрузки AssetsManager не запрашивал ресурсы.
        from .bingo_image_builder import BingoImageBuilder

        builder = BingoImageBuilder()
        # Тексты уже подготовлены в кеше. В экземпляр передаётся только
        # прогресс пользователя: галочка заменяет текст выполненной ячейки.
        for number in range(1, len(BINGO_TASKS) + 1):
            if number in completed_tasks:
                builder.with_check_mark(number)
        return builder.build()
