from aiogram.types import CallbackQuery, Message

from core.proxy.proxy_objects import CallbackQueryProxy, MessageProxy


class Mapper:
    """Преобразует события aiogram в объекты данных для core.

    Выполняет преобразование на границе Telegram-интеграции:
    извлекает только явно описанные поля и сохраняет отсутствие
    необязательных значений как None. Результат содержит значения
    стандартных типов Python и независим от исходного события.

    При добавлении поля в Proxy дополните соответствующий метод
    маппинга. Преобразование не вызывает Telegram API.
    """

    @staticmethod
    def map_message(message: Message) -> MessageProxy:
        """Создаёт снимок данных входящего сообщения.

        Args:
            message: Сообщение aiogram любого типа содержимого.

        Returns:
            Данные для core. Отсутствующие отправитель и текст
            представлены значением None.
        """
        return MessageProxy(
            message_id=message.message_id,
            chat_id=message.chat.id,
            user_id=message.from_user.id if message.from_user is not None else None,
            text=message.text,
        )

    @staticmethod
    def map_callback_query(callback_query: CallbackQuery) -> CallbackQueryProxy:
        """Создаёт снимок данных нажатия inline-кнопки.

        Args:
            callback_query: Callback aiogram с сообщением или без него.

        Returns:
            Данные для core. Если исходное сообщение отсутствует,
            chat_id и message_id равны None. Для недоступного
            сообщения сохраняются его идентификаторы.
        """
        message = callback_query.message
        return CallbackQueryProxy(
            query_id=callback_query.id,
            user_id=callback_query.from_user.id,
            data=callback_query.data,
            chat_id=message.chat.id if message is not None else None,
            message_id=message.message_id if message is not None else None,
        )
