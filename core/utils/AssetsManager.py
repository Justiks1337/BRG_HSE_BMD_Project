"""Загрузка ресурсов бота в память без зависимости от Telegram-библиотеки.

Ресурсы читаются из resources в корне проекта. Кэш хранит неизменяемые
байты, а получатели работают с отдельными буферами BytesIO.
"""

from io import BytesIO
from pathlib import Path

from .singleton import Singleton


class AssetsManager(Singleton):
    """Хранит общий кэш файлов из resources, включая вложенные каталоги.

    Перед получением ресурса вызовите load_assets. Ключом служит путь
    относительно resources с разделителем /, например d5/point_1.png.
    Все файлы загружаются как байты независимо от расширения. Повторный
    вызов load_assets обновляет кэш, удаляя из него исчезнувшие файлы.
    """

    def init(self) -> None:
        """Создаёт незагруженный кэш при первом создании Singleton.

        None отличает отсутствие загрузки от успешно загруженного пустого
        каталога. Повторное получение Singleton не сбрасывает состояние.
        """
        self._assets: dict[str, bytes] | None = None

    def load_assets(self) -> None:
        """Читает все файлы resources и заменяет кэш после успешной загрузки.

        Путь вычисляется относительно этого модуля и не зависит от рабочей
        директории процесса. Вложенные папки сохраняются в ключах, поэтому
        одинаковые имена файлов в разных папках не конфликтуют. Ошибка
        чтения любого файла оставляет предыдущий кэш без изменений.

        Raises:
            FileNotFoundError: Если resources отсутствует или файл исчез
                во время загрузки.
            NotADirectoryError: Если resources существует, но не каталог.
            OSError: Если каталог или один из файлов нельзя прочитать.
        """
        resources_dir = Path(__file__).resolve().parents[2] / "resources"
        if not resources_dir.exists():
            raise FileNotFoundError(f"Каталог ресурсов не найден: {resources_dir}")
        if not resources_dir.is_dir():
            raise NotADirectoryError(f"Путь ресурсов не является каталогом: {resources_dir}")

        assets = {}
        for path in sorted(resources_dir.rglob("*")):
            if path.is_file():
                filename = path.relative_to(resources_dir).as_posix()
                assets[filename] = path.read_bytes()
        # Публикуем новый кэш только после чтения всех ресурсов.
        self._assets = assets

    def get_assets(self, filename: str) -> BytesIO:
        """Возвращает отдельный буфер ресурса с позицией курсора в начале.

        Args:
            filename: Путь относительно resources, например bingo/image.png.
                Регистр учитывается; разделителем вложенных папок служит /.

        Returns:
            Новый BytesIO, подходящий для ResponseBuilder.with_image.
            Изменение или закрытие буфера не влияет на кэш и другие ответы.
            Чтение файлов с диска при получении ресурса не выполняется.

        Raises:
            RuntimeError: Если load_assets ещё не завершился успешно.
            FileNotFoundError: Если указанного пути нет в загруженном кэше.
        """
        if self._assets is None:
            raise RuntimeError("Ресурсы не загружены: сначала вызовите load_assets()")
        try:
            data = self._assets[filename]
        except KeyError as error:
            raise FileNotFoundError(f"Ресурс не найден в кэше: {filename}") from error
        return BytesIO(data)
