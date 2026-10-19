"""Публичные Proxy и отложенные экспорты роутеров core.

Импорт пакета не загружает конфигурацию заданий и их изображения.
Это позволяет сначала подготовить AssetsManager, затем импортировать
роутеры, чьи задания используют готовые буферы ресурсов.
"""

from .proxy import (
    ButtonProxy,
    CallbackQueryProxy,
    MessageProxy,
    ResponseBuilder,
    ResponseProxy,
)

__all__ = [
    "ButtonProxy",
    "ButtonRouter",
    "CallbackQueryProxy",
    "MessageProxy",
    "MessageRouter",
    "ResponseBuilder",
    "ResponseProxy",
]


def __getattr__(name: str) -> type:
    """Загружает публичные классы роутеров только при обращении к ним.

    Args:
        name: Имя экспортируемого класса ButtonRouter или MessageRouter.

    Returns:
        Запрошенный класс роутера с сохранением прежнего публичного API.

    Raises:
        AttributeError: Если запрошенное имя не экспортируется пакетом.
    """
    if name in ("ButtonRouter", "MessageRouter"):
        from .routing.router import ButtonRouter, MessageRouter

        return ButtonRouter if name == "ButtonRouter" else MessageRouter
    raise AttributeError(f"Модуль {__name__!r} не содержит атрибут {name!r}")
