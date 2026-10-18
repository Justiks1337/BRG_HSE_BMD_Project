"""Независимые от aiogram данные входящих событий и ответов пользователю."""

from dataclasses import dataclass
from io import BytesIO


@dataclass(frozen=True, slots=True)
class MessageProxy:
    """Передаёт данные сообщения в бизнес-логику приложения.

    Хранит независимый снимок значений стандартных типов Python.
    Набор полей расширяется по потребностям core вместе с Mapper.

    Attributes:
        message_id: Идентификатор сообщения внутри чата.
        chat_id: Идентификатор чата, в котором получено сообщение.
        user_id: Идентификатор отправителя, если он указан.
        text: Текст сообщения; None для сообщений без текста.
        is_private: Признак личного чата; по умолчанию False.
        photo_file_id: Идентификатор полученной фотографии либо None.
            Содержит строку, а не объект aiogram; сам файл не скачивается.
    """

    message_id: int
    chat_id: int
    user_id: int | None = None
    text: str | None = None
    is_private: bool = False
    photo_file_id: str | None = None


@dataclass(frozen=True, slots=True)
class CallbackQueryProxy:
    """Передаёт данные нажатия inline-кнопки в бизнес-логику.

    Содержит значения стандартных типов Python. Идентификаторы чата
    и сообщения доступны, только если callback связан с сообщением
    в чате. Набор полей расширяется по потребностям core.

    Attributes:
        query_id: Идентификатор callback для подтверждения обработки.
        user_id: Идентификатор пользователя, нажавшего кнопку.
        data: Данные кнопки, если они переданы.
        chat_id: Идентификатор чата исходного сообщения, если доступен.
        message_id: Идентификатор исходного сообщения, если доступен.
        is_private: True, если подтверждён личный чат исходного сообщения.
    """

    query_id: str
    user_id: int
    data: str | None = None
    chat_id: int | None = None
    message_id: int | None = None
    is_private: bool = False


@dataclass(frozen=True, slots=True)
class ButtonProxy:
    """Описывает inline-кнопку независимо от Telegram-библиотеки.

    callback_data хранит идентификатор действия внутри core. Если
    disabled=True, Telegram-слой создаёт неактивную кнопку и не
    передаёт этот идентификатор клиенту как callback_data.
    Надписи inline-кнопок не поддерживают HTML-разметку и parse_mode
    в Telegram API; HTML применяется к сообщениям, отправленным в ответ.
    Для custom emoji перед надписью используется отдельный идентификатор.

    Attributes:
        text: Надпись на кнопке обычным текстом, без HTML-разметки.
        callback_data: Данные, передаваемые при нажатии кнопки.
        disabled: Признак неактивной кнопки.
        icon_custom_emoji_id: Идентификатор custom emoji перед надписью.
            None означает отсутствие иконки. Это обычная строка без aiogram.
    """

    text: str
    callback_data: str
    disabled: bool = False
    icon_custom_emoji_id: str | None = None


@dataclass(frozen=True, slots=True)
class ResponseProxy:
    """Хранит подготовленный ответ пользователю.

    Создаётся через ResponseBuilder. Кнопки организованы в строки.
    Каждый ответ получает отдельный буфер изображения. Последующая
    настройка Builder не изменяет уже собранные ответы.

    Attributes:
        text: Текст ответа, если задан.
        buttons: Строки inline-кнопок; пустой кортеж означает отсутствие.
        image: Буфер изображения, если задано; содержимое изменяемо.
        parse_mode: Режим текста или подписи: HTML по умолчанию,
            MarkdownV2, Markdown либо None для отключения разметки.
            Хранится обычной строкой, независимо от типов aiogram.
    """

    text: str | None = None
    buttons: tuple[tuple[ButtonProxy, ...], ...] = ()
    image: BytesIO | None = None
    parse_mode: str | None = "HTML"
