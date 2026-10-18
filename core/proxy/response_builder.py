"""Пошаговая сборка ответов с текстом, изображением, кнопками и разметкой."""

from io import BytesIO

from core.proxy.proxy_objects import ButtonProxy, ResponseProxy


class ResponseBuilder:
    """Пошагово собирает ответ пользователю по паттерну Builder.

    Методы настройки возвращают текущий Builder для цепочки вызовов.
    build создаёт независимый снимок: дальнейшая настройка Builder
    не изменяет уже собранные ответы. Повторный build сохраняет
    текущие настройки. По умолчанию используется HTML; with_parse_mode
    позволяет изменить режим для конкретного ответа или отключить разметку.

    Example:
        image = BytesIO(image_bytes)
        response = (
            ResponseBuilder()
            .with_text("Выберите действие")
            .with_image(image)
            .add_button_row(ButtonProxy("Начать", "start"))
            .build()
        )
    """

    def __init__(self) -> None:
        """Готовит пустой ответ с HTML-форматированием по умолчанию."""
        self._parse_mode: str | None = "HTML"
        self._text: str | None = None
        self._image: bytes | None = None
        self._buttons: list[tuple[ButtonProxy, ...]] = []

    def with_text(self, text: str) -> "ResponseBuilder":
        """Задаёт текст ответа, заменяя предыдущее значение."""
        self._text = text
        return self

    def with_parse_mode(self, parse_mode: str | None) -> "ResponseBuilder":
        """Задаёт форматирование текста или подписи к изображению.

        Args:
            parse_mode: HTML, MarkdownV2, Markdown либо None для обычного
                текста. None явно отключает общий режим Telegram-бота.

        Returns:
            Текущий Builder для продолжения настройки ответа.

        Raises:
            ValueError: Если передан неподдерживаемый режим форматирования.
        """
        if parse_mode not in ("HTML", "MarkdownV2", "Markdown", None):
            raise ValueError("Неизвестный режим форматирования")
        self._parse_mode = parse_mode
        return self

    def with_image(self, image: BytesIO) -> "ResponseBuilder":
        """Сохраняет содержимое буфера, заменяя предыдущее изображение.

        Читает весь буфер независимо от текущей позиции курсора.
        Изменение или закрытие исходного буфера не влияет на Builder.

        Raises:
            ValueError: Если буфер пуст.
        """
        data = image.getvalue()
        if not data:
            raise ValueError("Буфер изображения не должен быть пустым")
        self._image = data
        return self

    def add_button_row(self, *buttons: ButtonProxy) -> "ResponseBuilder":
        """Добавляет строку кнопок в порядке передачи аргументов.

        Raises:
            ValueError: Если не передано ни одной кнопки.
        """
        if not buttons:
            raise ValueError("Строка должна содержать хотя бы одну кнопку")
        self._buttons.append(buttons)
        return self

    def build(self) -> ResponseProxy:
        """Создаёт ответ из текущих настроек Builder.

        Raises:
            ValueError: Если не заданы текст и изображение.
        """
        if not self._text and not self._image:
            raise ValueError("Ответ должен содержать текст или изображение")
        return ResponseProxy(
            text=self._text,
            parse_mode=self._parse_mode,
            buttons=tuple(self._buttons),
            image=BytesIO(self._image) if self._image is not None else None,
        )
