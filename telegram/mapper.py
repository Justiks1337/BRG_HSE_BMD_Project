"""Преобразование данных между aiogram и независимыми объектами core."""

from aiogram.enums import ChatType
from aiogram.types import (
    CallbackQuery,
    DisabledButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from core.proxy.proxy_objects import ButtonProxy, CallbackQueryProxy, MessageProxy


class Mapper:
    """Преобразует события и кнопки на границе Telegram и core.

    Входящие события aiogram превращает в независимые снимки данных
    стандартных типов Python. Кнопки core преобразует в клавиатуру
    aiogram для исходящего ответа. Необязательные значения сохраняет
    как None; запросы к Telegram API не выполняет.

    При добавлении поля в Proxy дополните соответствующий метод
    маппинга. Зависимости от aiogram остаются в Telegram-слое.
    """

    @staticmethod
    def map_message(message: Message) -> MessageProxy:
        """Создаёт снимок данных входящего сообщения.

        Args:
            message: Сообщение aiogram любого типа содержимого.

        Returns:
            Данные для core. Отсутствующие отправитель и текст
            представлены значением None. is_private определяется
            по типу чата Telegram. Для фотографии передаётся file_id
            самого большого доступного размера без скачивания файла.
        """
        return MessageProxy(
            message_id=message.message_id,
            chat_id=message.chat.id,
            user_id=message.from_user.id if message.from_user is not None else None,
            text=message.text,
            is_private=message.chat.type == ChatType.PRIVATE,
            photo_file_id=message.photo[-1].file_id if message.photo else None,
        )

    @staticmethod
    def map_callback_query(callback_query: CallbackQuery) -> CallbackQueryProxy:
        """Создаёт снимок данных нажатия inline-кнопки.

        Args:
            callback_query: Callback aiogram с сообщением или без него.

        Returns:
            Данные для core. Если исходное сообщение отсутствует,
            chat_id и message_id равны None. Для недоступного
            сообщения сохраняются его идентификаторы. Без исходного
            сообщения is_private=False: тип чата подтвердить невозможно.
        """
        message = callback_query.message
        return CallbackQueryProxy(
            query_id=callback_query.id,
            user_id=callback_query.from_user.id,
            data=callback_query.data,
            chat_id=message.chat.id if message is not None else None,
            message_id=message.message_id if message is not None else None,
            is_private=(
                message is not None and message.chat.type == ChatType.PRIVATE
            ),
        )

    @staticmethod
    def map_buttons(
        buttons: tuple[tuple[ButtonProxy, ...], ...],
    ) -> InlineKeyboardMarkup | None:
        """Собирает inline-клавиатуру, сохраняя строки и порядок кнопок.

        Args:
            buttons: Строки кнопок из ResponseProxy. Для disabled-кнопки
                сохраняется надпись, но callback_data не передаётся.

        Returns:
            Клавиатура aiogram либо None, если кнопок нет.
        """
        if not buttons:
            return None
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=button.text,
                        # callback_data и disabled задают разные типы кнопки.
                        # Telegram получает только один из этих вариантов.
                        callback_data=None if button.disabled else button.callback_data,
                        disabled=DisabledButton() if button.disabled else None,
                    )
                    for button in row
                ]
                for row in buttons
            ]
        )
