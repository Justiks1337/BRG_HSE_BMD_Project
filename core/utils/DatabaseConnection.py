"""Асинхронный доступ к пользователям и прогрессу туристических маршрутов.

Все SQL-запросы приложения сосредоточены в DatabaseConnection; обработчики
маршрутов получают через него готовые значения шагов.
"""

from typing import Optional
import os

import aiosqlite
from dotenv import load_dotenv

from .singleton import Singleton


load_dotenv()


class DatabaseConnection(Singleton):
    """Обеспечивает взаимодействие с БД через единственный экземпляр.

    Использует паттерн Singleton. Инициализируйте объект и откройте соединение
    через get_connection перед запуском основной обработки сообщений.
    При завершении приложения закройте соединение методом close.

    Все операции взаимодействия с базой данных должны быть реализованы
    исключительно в этом классе. Он хранит запрещённые и доверенные
    сообщения, предупреждения и время регистрации участников.
    """

    def init(self):
        """Готовит состояние Singleton до открытия соединения с БД."""
        self.connect: Optional[aiosqlite.Connection] = None

    @property
    def connection(self) -> aiosqlite.Connection:
        """Возвращает открытое соединение.

        Raises:
            RuntimeError: Если соединение ещё не открыто или уже закрыто.
        """
        connection = self.connect
        if connection is None:
            raise RuntimeError("Соединение с БД не открыто или уже закрыто")
        return connection

    async def create_tables(self) -> None:
        """Создаёт таблицы пользователей, бинго и прогресса по линиям D1–D5.

        Таблицы d1–d5 хранят целочисленные user_id и step: 0 обозначает
        вступление, 1 — первую точку. Существующие шаги не перенумеровываются.
        Внешний ключ связывает каждую запись с users(user_id).
        photo_uploads хранит одно ожидание фотографии для бинго или маршрута.
        Старое ожидание из bingo_uploads переносится при первом запуске,
        после чего прежняя таблица удаляется. Каждый SQL-запрос
        выполняется с автоматической фиксацией изменений.
        """
        async with self.connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            ) 
        """):
            pass

        async with self.connection.execute("""
            CREATE TABLE IF NOT EXISTS bingo (
                user_id INTEGER NOT NULL ,
                task_number INTEGER NOT NULL, 
                FOREIGN KEY (user_id) 
                REFERENCES users(user_id)
            )
        """):
            pass

        async with self.connection.execute("""
            CREATE TABLE IF NOT EXISTS photo_uploads (
                user_id INTEGER PRIMARY KEY,
                target TEXT NOT NULL CHECK(target IN ('bingo', 'd1', 'd2', 'd3', 'd4', 'd5')),
                item_number INTEGER NOT NULL CHECK(item_number > 0),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """):
            pass

        # Сохраняем ранее выбранные задания бинго при обновлении схемы.
        async with self.connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'bingo_uploads'"
        ) as cursor:
            legacy_uploads = await cursor.fetchone()
        if legacy_uploads is not None:
            async with self.connection.execute("""
                INSERT INTO photo_uploads (user_id, target, item_number)
                SELECT user_id, 'bingo', task_number FROM bingo_uploads WHERE 1
                ON CONFLICT(user_id) DO NOTHING
            """):
                pass
            async with self.connection.execute("DROP TABLE bingo_uploads"):
                pass

        # Все линии используют одну схему; имена таблиц заданы в приложении.
        for table_name in ("d1", "d2", "d3", "d4", "d5"):
            async with self.connection.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    user_id INTEGER NOT NULL,
                    step INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """):
                pass

            # Раньше первая точка была доступна без записи в таблице.
            # Сохраняем начатый маршрут при наличии старого ожидания фото.
            async with self.connection.execute(f"""
                INSERT INTO {table_name} (user_id, step)
                SELECT user_id, 1 FROM photo_uploads
                WHERE target = ? AND item_number = 1 AND NOT EXISTS (
                    SELECT 1 FROM {table_name}
                    WHERE {table_name}.user_id = photo_uploads.user_id
                )
            """, (table_name,)):
                pass

    async def add_user(self, user_id: int) -> None:
        """
        Создать нового пользователя в базе данных.
        Может вызывать sqlite3.IntegrityError: constraint failed, в случае, если пользователь уже существует
        Обязательно проверяйте наличие пользователя в базе данных, перед использованием данного метода
        :param user_id: int, ID пользователя
        :return: None
        """
        async with self.connection.execute("""
            INSERT INTO users 
            VALUES (?)
            ON CONFLICT(user_id) DO NOTHING
        """, (user_id, )
        ):
            pass

    async def get_completed_bingo_tasks(self, user_id: int) -> set[int]:
        """Возвращает номера выполненных заданий бинго пользователя.

        Задание считается выполненным при наличии записи в таблице bingo.
        Повторные записи объединяются; возвращаются только номера 1–12.
        Метод читает данные и не меняет прогресс пользователя.

        Args:
            user_id: Идентификатор пользователя для выборки его заданий.

        Returns:
            Набор номеров выполненных клеток, доступный для формирования
            как клавиатуры, так и изображения. При отсутствии записей
            возвращает пустой набор.

        Raises:
            RuntimeError: Если соединение с БД не открыто.
        """
        async with self.connection.execute(
            "SELECT task_number FROM bingo "
            "WHERE user_id = ? AND task_number BETWEEN 1 AND 12",
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()
        return {row[0] for row in rows}

    async def request_bingo_upload(self, user_id: int, task_number: int) -> bool:
        """Сохраняет задание, которое выполнит следующая фотография.

        Пользователь создаётся при необходимости для соблюдения внешнего
        ключа. Новый выбор заменяет ожидание из бинго или маршрута.
        Выполненное задание не становится ожидающим даже при нажатии
        старой кнопки загрузки.

        Args:
            user_id: Идентификатор пользователя в личном чате.
            task_number: Целое число от 1 до 12.

        Returns:
            True, если ожидание сохранено; False, если задание выполнено.

        Raises:
            ValueError: Если номер задания некорректен.
            RuntimeError: Если соединение с БД не открыто.
        """
        if type(task_number) is not int or not 1 <= task_number <= 12:
            raise ValueError("Неизвестное задание бинго")
        await self.add_user(user_id)
        async with self.connection.execute("""
            INSERT INTO photo_uploads (user_id, target, item_number)
            SELECT ?, 'bingo', ?
            WHERE NOT EXISTS (
                SELECT 1 FROM bingo WHERE user_id = ? AND task_number = ?
            )
            ON CONFLICT(user_id) DO UPDATE SET
                target = excluded.target, item_number = excluded.item_number
            RETURNING item_number
        """, (user_id, task_number, user_id, task_number)) as cursor:
            row = await cursor.fetchone()
        return row is not None

    async def complete_bingo_upload(self, user_id: int) -> int | None:
        """Записывает выполнение ожидающего задания и снимает ожидание.

        Номер берётся из БД, а не из подписи фотографии. Один SQL-запрос
        проверяет ожидание и отсутствие выполнения перед вставкой: две
        одновременно обрабатываемые фотографии не дублируют выполнение.
        Изображение не сохраняется и его содержимое не проверяется.

        Args:
            user_id: Идентификатор отправителя фотографии из личного чата.

        Returns:
            Номер выполненного задания либо None, если нет ожидающего
            задания или оно уже было выполнено.

        Raises:
            RuntimeError: Если соединение с БД не открыто.
        """
        async with self.connection.execute("""
            INSERT INTO bingo (user_id, task_number)
            SELECT user_id, item_number FROM photo_uploads
            WHERE user_id = ? AND target = 'bingo' AND NOT EXISTS (
                SELECT 1 FROM bingo
                WHERE bingo.user_id = photo_uploads.user_id
                    AND bingo.task_number = photo_uploads.item_number
            )
            RETURNING task_number
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
        if row is not None:
            # Не стираем другое задание, выбранное во время обработки фото.
            async with self.connection.execute(
                "DELETE FROM photo_uploads "
                "WHERE user_id = ? AND target = 'bingo' AND item_number = ?",
                (user_id, row[0]),
            ):
                pass
        return row[0] if row is not None else None

    async def start_diameter(self, diameter: str, user_id: int) -> None:
        """Переводит новый маршрут с нулевого шага на первую точку.

        Если маршрут уже начат или завершён, ничего не меняет. Вставка
        проверяет текущий шаг в том же SQL-запросе, поэтому повторные
        и одновременные нажатия «Поехали» не дублируют запуск.

        Args:
            diameter: Имя таблицы d1–d5 из закрытого списка.
            user_id: Идентификатор пользователя, начинающего маршрут.

        Raises:
            ValueError: Если диаметр неизвестен.
            RuntimeError: Если соединение с БД не открыто.
        """
        if diameter not in ("d1", "d2", "d3", "d4", "d5"):
            raise ValueError("Неизвестный диаметр")
        await self.add_user(user_id)
        async with self.connection.execute(f"""
            INSERT INTO {diameter} (user_id, step)
            SELECT ?, 1 WHERE COALESCE((
                SELECT step FROM {diameter} WHERE user_id = ?
                ORDER BY rowid DESC LIMIT 1
            ), 0) = 0
        """, (user_id, user_id)):
            pass

    async def request_diameter_upload(
        self, user_id: int, diameter: str, step: int, final_step: int,
    ) -> bool:
        """Ожидает фото для текущей незавершённой точки маршрута.

        Новое ожидание заменяет прежнее, включая бинго. Номер из кнопки
        должен совпадать с прогрессом в БД; вступление и финал не требуют
        фотографии. До нажатия «Поехали» загрузка первой точки недоступна.

        Args:
            user_id: Идентификатор пользователя из личного чата.
            diameter: Имя таблицы d1–d5 из закрытого списка.
            step: Номер точки, на которой нажата кнопка загрузки.
            final_step: Номер финального поздравления в списке точек.

        Returns:
            True, если ожидание создано; False для старой или финальной точки.

        Raises:
            ValueError: Если диаметр неизвестен или номера шагов некорректны.
            RuntimeError: Если соединение с БД не открыто.
        """
        if diameter not in ("d1", "d2", "d3", "d4", "d5"):
            raise ValueError("Неизвестный диаметр")
        if any(type(value) is not int or value < 1 for value in (step, final_step)):
            raise ValueError("Шаг маршрута должен быть положительным целым числом")
        await self.add_user(user_id)
        # В SQL подставляется только проверенное имя таблицы; данные — через ?.
        async with self.connection.execute(f"""
            INSERT INTO photo_uploads (user_id, target, item_number)
            SELECT ?, ?, ?
            WHERE ? < ? AND ? = COALESCE((
                SELECT step FROM {diameter} WHERE user_id = ?
                ORDER BY rowid DESC LIMIT 1
            ), 0)
            ON CONFLICT(user_id) DO UPDATE SET
                target = excluded.target, item_number = excluded.item_number
            RETURNING item_number
        """, (user_id, diameter, step, step, final_step, step, user_id)) as cursor:
            row = await cursor.fetchone()
        return row is not None

    async def complete_diameter_upload(self, user_id: int) -> tuple[str, int] | None:
        """Сохраняет следующий шаг для ожидающей фотографии маршрута.

        История в таблицах d1–d5 сохраняется: новая строка становится текущей
        по существующему правилу последнего rowid. Вставка разрешена только
        при совпадении ожидающей точки с текущим шагом, поэтому повторные
        и одновременно полученные фотографии не пропускают точки.

        Args:
            user_id: Идентификатор отправителя фотографии из личного чата.

        Returns:
            Диаметр и новый шаг либо None при отсутствии актуального ожидания.

        Raises:
            RuntimeError: Если соединение с БД не открыто.
        """
        async with self.connection.execute("""
            SELECT target, item_number FROM photo_uploads
            WHERE user_id = ? AND target IN ('d1', 'd2', 'd3', 'd4', 'd5')
        """, (user_id,)) as cursor:
            pending = await cursor.fetchone()
        if pending is None:
            return None
        diameter, step = pending
        # diameter выбран из закрытого списка в SELECT выше.
        async with self.connection.execute(f"""
            INSERT INTO {diameter} (user_id, step)
            SELECT user_id, item_number + 1 FROM photo_uploads
            WHERE user_id = ? AND target = ? AND item_number = ?
                AND item_number = COALESCE((
                    SELECT step FROM {diameter} WHERE user_id = ?
                    ORDER BY rowid DESC LIMIT 1
                ), 0)
            RETURNING step
        """, (user_id, diameter, step, user_id)) as cursor:
            row = await cursor.fetchone()
        # Удаляем только обработанное ожидание, сохраняя более новый выбор.
        async with self.connection.execute(
            "DELETE FROM photo_uploads WHERE user_id = ? AND target = ? AND item_number = ?",
            (user_id, diameter, step),
        ):
            pass
        return (diameter, row[0]) if row is not None else None

    async def get_diameter_step(self, diameter: str, user_id: int) -> int:
        """Возвращает сохранённый шаг пользователя на выбранном диаметре.

        Args:
            diameter: Имя таблицы из фиксированного списка d1–d5.
            user_id: Идентификатор пользователя, переданный параметром SQL.

        Returns:
            Последний записанный шаг. Если прогресса ещё нет, возвращает 0
            для вступления без изменения БД. При нескольких записях выбирает
            последнюю по rowid, то есть по порядку добавления записей.

        Raises:
            ValueError: Если диаметр неизвестен или сохранённый step
                не является неотрицательным целым числом.
            RuntimeError: Если соединение с БД не открыто.
        """
        # SQL-параметры нельзя использовать для имён таблиц. Поэтому
        # интерполируем только имя из закрытого списка, а user_id — через ?.
        if diameter not in ("d1", "d2", "d3", "d4", "d5"):
            raise ValueError("Неизвестный диаметр")
        async with self.connection.execute(
            f"SELECT step FROM {diameter} WHERE user_id = ? "
            "ORDER BY rowid DESC LIMIT 1",
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()
        if row is None:
            return 0
        step = row[0]
        if not isinstance(step, int) or step < 0:
            raise ValueError("Шаг маршрута должен быть неотрицательным целым числом")
        return step

    async def get_connection(self):
        """Открывает соединение с autocommit и проверкой внешних ключей.

        SQLite фиксирует изменения после завершения каждого SQL-запроса.
        Несколько запросов одного метода не объединяются в транзакцию.
        Внешние ключи включаются до создания и миграции таблиц.
        """
        self.connect = await aiosqlite.connect(
            os.environ["DATABASE_NAME"], autocommit=True,
        )
        # SQLite требует включать внешние ключи для каждого соединения
        # до начала транзакций, иначе PRAGMA не изменит настройку.
        async with self.connection.execute("PRAGMA foreign_keys = ON"):
            pass
        await self.create_tables()


    async def close(self):
        """
        Закрытие сессии aiosqlite
        Так как сессия открывается один раз при запуске бота, она никогда не закрывается
        Из-за этого процесс нужно очень неаккуратно убивать.

        Это плохая практика, поэтому вызывайте это перед завершением процесса
        :return: None
        """

        if self.connect is not None:
            await self.connect.close()
            self.connect = None
