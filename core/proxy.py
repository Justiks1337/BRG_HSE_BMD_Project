from dataclasses import dataclass


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
    """

    message_id: int
    chat_id: int
    user_id: int | None = None
    text: str | None = None


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
    """

    query_id: str
    user_id: int
    data: str | None = None
    chat_id: int | None = None
    message_id: int | None = None
