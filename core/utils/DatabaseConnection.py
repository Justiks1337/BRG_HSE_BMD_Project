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
        self.connect: Optional[aiosqlite.Connection] = None

    @property
    def connection(self) -> aiosqlite.Connection:
        connection = self.connect
        if connection is None:
            raise RuntimeError("Соединение с БД не открыто или уже закрыто")
        return connection

    async def create_tables(self) -> None:
        """Создаёт таблицы пользователей, бинго и прогресса по линиям D1–D5.

        Таблицы d1–d5 хранят целочисленные user_id и step.
        Внешний ключ связывает каждую запись с users(user_id).
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

        await self.connection.commit()

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

        await self.connection.commit()

    async def get_connection(self):
        """Открывает соединение с проверкой внешних ключей и создаёт таблицы."""
        self.connect = await aiosqlite.connect(os.environ["DATABASE_NAME"])
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
