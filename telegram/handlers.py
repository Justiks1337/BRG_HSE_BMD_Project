"""Связывает Telegram-события с core и отправляет подготовленные ответы.

Выбор команды и проверку callback выполняют роутеры core через Proxy.
Ответы команд и нажатий отправляются как сообщения с текстом, изображением
и клавиатурой, а подтверждение callback снимает индикатор ожидания.
"""

from aiogram import Router
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from core.proxy import ResponseProxy
from core.routing.router import ButtonRouter, MessageRouter
from .mapper import Mapper


router = Router()
message_router = MessageRouter()
button_router = ButtonRouter()


async def _send_response(message: Message, response: ResponseProxy) -> None:
    """Отправляет ответ core в чат исходного сообщения.

    Args:
        message: Сообщение aiogram, определяющее чат получателя.
        response: Текст, изображение и кнопки ответа. При наличии картинки
            текст становится подписью. Содержимое буфера читается целиком,
            независимо от позиции его курсора.
    """
    keyboard = Mapper.map_buttons(response.buttons)
    if response.image is not None:
        await message.answer_photo(
            photo=BufferedInputFile(response.image.getvalue(), filename="image.png"),
            caption=response.text,
            reply_markup=keyboard,
        )
    elif response.text is not None:
        await message.answer(response.text, reply_markup=keyboard)


@router.message()
async def handle_message(message: Message) -> None:
    """Передаёт сообщение в core и отправляет подготовленный ответ.

    Args:
        message: Входящее сообщение любого типа содержимого. Если роутер
            вернул None, новое сообщение пользователю не отправляется.
    """
    response = await message_router.route(Mapper.map_message(message))
    if response is not None:
        await _send_response(message, response)


@router.callback_query()
async def handle_callback_query(callback_query: CallbackQuery) -> None:
    """Подтверждает нажатие и отправляет выбранную точку новым сообщением.

    Args:
        callback_query: Событие нажатия кнопки. Callback без доступного
            исходного сообщения только подтверждается. Неизвестные кнопки
            и события вне личного чата отклоняются роутером core.
    """
    # Подтверждаем до чтения БД, чтобы клиент не ждал завершения обработки.
    await callback_query.answer()
    if not isinstance(callback_query.message, Message):
        return
    response = await button_router.route(Mapper.map_callback_query(callback_query))
    if response is not None:
        # Callback-уведомление не поддерживает картинку и клавиатуру,
        # поэтому полноценную точку отправляем отдельным сообщением.
        await _send_response(callback_query.message, response)
