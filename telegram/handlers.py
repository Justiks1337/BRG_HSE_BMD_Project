"""Связывает Telegram-события с core и отправляет подготовленные ответы.

Общие хендлеры не используют фильтры aiogram: выбор команды и проверку
идентификаторов кнопок выполняют роутеры core через объекты Proxy.
"""

from aiogram import Router
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from core.routing.router import ButtonRouter, MessageRouter
from .mapper import Mapper


router = Router()
message_router = MessageRouter()
button_router = ButtonRouter()


@router.message()
async def handle_message(message: Message) -> None:
    """Передаёт сообщение в core и отправляет его ответ в исходный чат.

    Если роутер вернул None, сообщение остаётся без ответа. Для
    изображения текст используется как подпись; строки кнопок
    преобразуются в inline-клавиатуру через Mapper.

    Args:
        message: Входящее сообщение aiogram любого типа содержимого.
    """
    response = await message_router.route(Mapper.map_message(message))
    if response is None:
        return

    keyboard = Mapper.map_buttons(response.buttons)
    if response.image is not None:
        # getvalue() берёт весь буфер, независимо от позиции курсора.
        # Обёртка aiogram создаётся здесь, сохраняя core независимым.
        await message.answer_photo(
            photo=BufferedInputFile(response.image.getvalue(), filename="image.png"),
            caption=response.text,
            reply_markup=keyboard,
        )
    elif response.text is not None:
        await message.answer(response.text, reply_markup=keyboard)


@router.callback_query()
async def handle_callback_query(callback_query: CallbackQuery) -> None:
    """Передаёт нажатие в core и подтверждает обработанный callback.

    Отключённые маршруты не возвращают ответ. Неизвестные callback
    также подтверждаются без уведомления и изменения сообщения.

    Args:
        callback_query: Событие нажатия, в том числе без сообщения.
    """
    response = await button_router.route(Mapper.map_callback_query(callback_query))
    # Подтверждение убирает индикатор ожидания у клиента Telegram.
    await callback_query.answer(text=response.text if response is not None else None)
