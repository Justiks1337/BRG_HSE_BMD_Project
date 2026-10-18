"""Собирает PNG-карточку бинго из текстов и галочек в двенадцати ячейках.

Изображения берутся из уже загруженного AssetsManager при импорте модуля.
Перед началом polling метод prepare_images готовит общую галочку и
двенадцать фрагментов с постоянными текстами из BINGO_TASKS. Подготовка
выполняется в рабочем потоке после загрузки ресурсов. Каждый build
использует готовый кеш и возвращает независимый PNG-буфер.
"""

from io import BytesIO
from math import floor

from PIL import Image, ImageDraw, ImageFont

from ...utils.AssetsManager import AssetsManager
from .content import BINGO_TASKS


class BingoImageBuilder:
    """Размещает текст или check_mark по центрам ячеек сетки 3×4.

    Ячейки нумеруются от 1 до 12 слева направо, сверху вниз. По умолчанию
    каждая содержит свой постоянный текст задания. Выполненные ячейки
    заменяются галочками. Готовые фрагменты общие для всех пользователей
    и используются только для чтения; прогресс хранится в экземпляре.
    До первой сборки необходимо вызвать prepare_images при запуске бота.

    Attributes:
        ceil_coords: Координаты центров двенадцати ячеек в пикселях.
        check_image: Буфер фонового изображения bingo.png из памяти.
        check_mark: Буфер изображения галочки check.png из памяти.
    """

    ceil_coords: tuple[tuple[float, float], ...] = (
        (205.5, 530),
        (487.5, 530),
        (766.5, 530),
        (1048, 530),
        (205.5, 738),
        (487.5, 738),
        (766.5, 738),
        (1048, 738),
        (205.5, 940),
        (487.5, 940),
        (766.5, 940),
        (1048, 940),
    )

    check_image: BytesIO = AssetsManager().get_assets("bingo.png")
    check_mark: BytesIO = AssetsManager().get_assets("check.png")

    _cell_size = (240, 160)
    _line_spacing = 4

    _prepared_mark: Image.Image
    _text_tiles: tuple[tuple[Image.Image, tuple[int, int]], ...]

    def __init__(self) -> None:
        """Создаёт карточку с текстами всех заданий и без отметок выполнения.

        Изображения и шрифт повторно не загружаются. Экземпляр хранит только
        номера выполненных ячеек, поэтому прогресс пользователей не смешивается.
        """
        self._completed_cells: set[int] = set()

    def with_check_mark(self, cell_number: int) -> "BingoImageBuilder":
        """Отмечает выполненную ячейку для замены её текста галочкой.

        Args:
            cell_number: Номер ячейки от 1 до 12.

        Returns:
            Текущий Builder для продолжения настройки.

        Raises:
            ValueError: Если номер ячейки некорректен.
        """
        self._validate_cell(cell_number)
        self._completed_cells.add(cell_number)
        return self

    def build(self) -> BytesIO:
        """Собирает карточку из готовых текстовых ячеек и одной общей галочки.

        При каждом вызове декодируется отдельный фон и выбирается содержимое
        двенадцати ячеек. Шрифт, переносы текста и масштаб галочки уже подготовлены
        при запуске приложения и не пересчитываются. Общие изображения не меняются.

        Returns:
            Новый BytesIO с PNG и курсором в начале, пригодный для
            ResponseBuilder.with_image. Без отметок отображаются все задания.

        Raises:
            OSError: Если фоновое изображение невозможно прочитать.
        """
        with Image.open(BytesIO(self.check_image.getvalue())) as source:
            image = source.convert("RGBA")
        mark = self._prepared_mark
        for cell_number, (tile, position) in enumerate(self._text_tiles, 1):
            if cell_number in self._completed_cells:
                center = self.ceil_coords[cell_number - 1]
                mark_position = (
                    round(center[0] - mark.width / 2),
                    round(center[1] - mark.height / 2),
                )
                image.alpha_composite(mark, mark_position)
            else:
                # Фрагмент содержит исходный фон и готовый текст. Вставка
                # целиком сохраняет цвета сглаженных краёв букв.
                image.paste(tile, position)

        result = BytesIO()
        image.save(result, format="PNG")
        result.seek(0)
        return result

    @classmethod
    def prepare_images(cls) -> None:
        """Один раз готовит общую галочку и двенадцать текстовых фрагментов.

        Вызывается один раз при запуске приложения через asyncio.to_thread,
        после загрузки AssetsManager и до начала polling. Во время обработки
        сообщений кеш только читается: блокировки и вытеснение не нужны.
        Тексты, фон и шрифт считаются постоянными до перезапуска приложения.
        Сначала используется системный DejaVuSans.ttf. Если он недоступен,
        резервный шрифт берётся из resources/fonts через AssetsManager.
        Шрифт и временный фон освобождаются после подготовки изображений.

        Raises:
            OSError: Если ресурс или фиксированный шрифт недоступен.
            ValueError: Если галочка прозрачна, число заданий не совпадает
                с числом ячеек или текст не помещается в свою ячейку.
        """
        with Image.open(BytesIO(cls.check_mark.getvalue())) as source:
            mark = source.convert("RGBA")
        bounds = mark.getbbox()
        if bounds is None:
            raise ValueError("Изображение галочки полностью прозрачно")
        mark = mark.crop(bounds)
        mark.thumbnail(cls._cell_size, Image.Resampling.LANCZOS)

        with Image.open(BytesIO(cls.check_image.getvalue())) as source:
            background = source.convert("RGBA")
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 32)
        except OSError:
            # Резервная копия уже загружена в память при запуске бота.
            font = ImageFont.truetype(
                AssetsManager().get_assets("fonts/DejaVuSans.ttf"), 32,
            )
        tiles = []
        for center, text in zip(cls.ceil_coords, BINGO_TASKS, strict=True):
            # Запас по два пикселя сохраняет сглаживание у краёв ячейки.
            left = floor(center[0] - cls._cell_size[0] / 2) - 2
            top = floor(center[1] - cls._cell_size[1] / 2) - 2
            tile = background.crop((
                left, top,
                left + cls._cell_size[0] + 4,
                top + cls._cell_size[1] + 4,
            ))
            cls._draw_text(
                ImageDraw.Draw(tile), (center[0] - left, center[1] - top), text, font,
            )
            tiles.append((tile, (left, top)))
        cls._prepared_mark = mark
        cls._text_tiles = tuple(tiles)

    def _validate_cell(self, cell_number: int) -> None:
        """Проверяет номер ячейки перед изменением состояния Builder.

        Args:
            cell_number: Целочисленный номер от 1 до 12; bool не допускается.

        Raises:
            ValueError: Если номер нецелый или выходит за границы сетки.
        """
        if type(cell_number) is not int or not 1 <= cell_number <= len(self.ceil_coords):
            raise ValueError("Номер ячейки должен быть целым числом от 1 до 12")

    @classmethod
    def _wrap_text(
        cls, draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
    ) -> str:
        """Переносит слова по ширине ячейки, сохраняя явные переводы строк.

        Args:
            draw: Контекст Pillow для измерения реальной ширины текста.
            text: Исходный текст ячейки.
            font: Шрифт текущего проверяемого размера.

        Returns:
            Текст со строками шириной не более ячейки, кроме отдельных
            слишком длинных слов: их проверяет _draw_text при подборе размера.
        """
        lines = []
        for paragraph in text.split("\n"):
            line = ""
            for word in paragraph.split():
                candidate = f"{line} {word}" if line else word
                if line and draw.textlength(candidate, font=font) > cls._cell_size[0]:
                    lines.append(line)
                    line = word
                else:
                    line = candidate
            lines.append(line)
        return "\n".join(lines)

    @classmethod
    def _draw_text(
        cls, draw: ImageDraw.ImageDraw, center: tuple[float, float], text: str,
        base_font: ImageFont.FreeTypeFont,
    ) -> None:
        """Подбирает размер шрифта и центрирует текст внутри области ячейки.

        Args:
            draw: Контекст рисования на фрагменте исходного фона.
            center: Центр ячейки относительно подготовленного фрагмента.
            text: Постоянный текст задания для отрисовки белым цветом.
            base_font: Общий шрифт, используемый только во время подготовки.

        Raises:
            ValueError: Если текст не помещается при размере шрифта 12.
        """
        if not text.strip():
            return
        for size in range(32, 11, -1):
            font = base_font.font_variant(size=size)
            wrapped = cls._wrap_text(draw, text, font)
            left, top, right, bottom = draw.multiline_textbbox(
                (0, 0), wrapped, font=font, spacing=cls._line_spacing, align="center",
            )
            width, height = right - left, bottom - top
            if width <= cls._cell_size[0] and height <= cls._cell_size[1]:
                position = (center[0] - width / 2 - left, center[1] - height / 2 - top)
                draw.multiline_text(
                    position, wrapped, font=font, fill="white",
                    spacing=cls._line_spacing, align="center",
                )
                return
        raise ValueError("Текст не помещается в ячейку бинго")
