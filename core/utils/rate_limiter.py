"""Ограничение частоты действий пользователя без зависимости от Telegram.

История хранится в памяти процесса. Скользящее окно учитывает только
разрешённые действия; отклонённый спам не продлевает время ограничения.
"""

from collections import OrderedDict, deque
from math import isfinite
from time import monotonic


class RateLimiter:
    """Разрешает ограниченное число действий каждого пользователя за интервал.

    История пользователей упорядочена по последнему разрешённому действию.
    Просроченные записи удаляются при следующей проверке. Число пользователей
    и длина их очередей ограничены, поэтому история не растёт бесконечно.
    Метод allow синхронный и вызывается из одного потока цикла asyncio:
    проверка и регистрация действия выполняются без переключения корутин.
    """

    def __init__(
        self, limit: int = 10, window_seconds: float = 10.0,
        max_users: int = 10_000,
    ) -> None:
        """Создаёт пустую историю с заданным лимитом и скользящим окном.

        Args:
            limit: Максимальное число разрешённых действий в одном окне.
            window_seconds: Длина окна в секундах по монотонным часам.
            max_users: Максимум активных пользователей в истории. При
                заполнении новые пользователи временно отклоняются до
                освобождения просроченных записей.

        Raises:
            ValueError: Если лимиты не являются положительными целыми
                или окно неположительное либо бесконечное.
        """
        if type(limit) is not int or limit < 1:
            raise ValueError("Лимит действий должен быть положительным целым числом")
        if not isfinite(window_seconds) or window_seconds <= 0:
            raise ValueError("Интервал должен быть положительным конечным числом")
        if type(max_users) is not int or max_users < 1:
            raise ValueError("Лимит пользователей должен быть положительным целым числом")
        self._limit = limit
        self._window_seconds = window_seconds
        self._max_users = max_users
        self._requests: OrderedDict[int, deque[float]] = OrderedDict()

    def allow(self, user_id: int) -> bool:
        """Проверяет частоту и регистрирует действие, если оно разрешено.

        Args:
            user_id: Идентификатор пользователя; все его защищённые действия
                используют одну очередь независимо от команды и кнопки.

        Returns:
            True, если действие разрешено. False при превышении частоты
            или заполнении истории новыми пользователями. Записи на точной
            границе окна считаются истёкшими. Отклонения в очередь не входят.
        """
        now = monotonic()
        cutoff = now - self._window_seconds
        # Последние действия упорядочены: после первой свежей записи
        # остальные пользователи тоже ещё находятся внутри окна.
        while self._requests:
            oldest = next(iter(self._requests.values()))
            if oldest[-1] > cutoff:
                break
            self._requests.popitem(last=False)

        requests = self._requests.get(user_id)
        if requests is None:
            if len(self._requests) >= self._max_users:
                return False
            requests = deque()
            self._requests[user_id] = requests
        while requests and requests[0] <= cutoff:
            requests.popleft()
        if len(requests) >= self._limit:
            return False
        requests.append(now)
        self._requests.move_to_end(user_id)
        return True
