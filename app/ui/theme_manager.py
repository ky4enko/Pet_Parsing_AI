from PySide6.QtCore import QObject, QSettings, Qt, QRectF
from PySide6.QtGui import QPixmap, QPainter, QColor
from pathlib import Path
from PySide6.QtGui import QPixmap, QImageReader
from PySide6.QtCore import QObject, QSettings, Qt
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import (
    QGraphicsBlurEffect,
    QGraphicsPixmapItem,
    QGraphicsScene,
)


class ThemeManager(QObject):

    def __init__(self):
        super().__init__()

        # Папка с фоновыми изображениями: app/ui/assets
        self.background_dir = (
                Path(__file__).resolve().parent / "assets"
        )

        self.settings = QSettings(
            "PetParsingAI",
            "ThemeSettings"
        )

        self.blur_radius = self.settings.value(
            "blur_radius", 18, type=int
        )

        self.darkness = self.settings.value(
            "darkness", 110, type=int
        )

        self.themes = self.load_themes()

        saved_theme = self.settings.value(
            "current_theme", 1, type=int
        )

        self.current_theme = (
            saved_theme if saved_theme in self.themes
            else next(iter(self.themes), 1)
        )

        print("\n========== THEMES ==========")
        print("Папка фонов:", self.background_dir)

        if self.themes:
            for number, theme in self.themes.items():
                print(f"Найдено: {theme['path']}")
        else:
            print("Фоновые изображения не найдены!")

        print("============================\n")

    def load_themes(self):
        themes = {}

        for number in range(1, 6):
            image_path = (
                self.background_dir / f"background{number}.jpg"
            )

            if image_path.is_file():
                pixmap = QPixmap(str(image_path))

                if not pixmap.isNull():
                    themes[number] = {
                        "name": f"Стиль {number}",
                        "path": image_path,
                    }

        return themes

    def get_themes(self):
        return self.themes

    def set_theme(self, theme_number):
        if theme_number not in self.themes:
            return False

        self.current_theme = theme_number

        self.settings.setValue(
            "current_theme",
            theme_number
        )

        return True

    def set_blur(self, value):
        self.blur_radius = max(0, min(40, int(value)))

        self.settings.setValue(
            "blur_radius",
            self.blur_radius
        )

    def set_darkness(self, value):
        self.darkness = max(0, min(220, int(value)))

        self.settings.setValue(
            "darkness",
            self.darkness
        )

    def get_darkness(self):
        return self.darkness

    def get_background_pixmap(self, size=None):
        theme = self.themes.get(self.current_theme)

        if theme is None:
            return QPixmap()

        reader = QImageReader(str(theme["path"]))
        reader.setAutoTransform(True)

        image = reader.read()

        if image.isNull():
            print("Ошибка загрузки изображения:", reader.errorString())
            return QPixmap()

        pixmap = QPixmap.fromImage(image)

        if pixmap.isNull():
            return QPixmap()

        # Масштабируем без искажения пропорций
        if size is not None and size.isValid():
            pixmap = pixmap.scaled(
                size,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            # Обрезаем лишнее по центру
            x = max(0, (pixmap.width() - size.width()) // 2)
            y = max(0, (pixmap.height() - size.height()) // 2)

            pixmap = pixmap.copy(
                x, y,
                size.width(),
                size.height()
            )

        # Размытие
        if self.blur_radius > 0:
            padding = self.blur_radius * 2

            scene = QGraphicsScene()
            item = QGraphicsPixmapItem(pixmap)
            item.setOffset(padding, padding)

            blur = QGraphicsBlurEffect()
            blur.setBlurRadius(self.blur_radius)
            item.setGraphicsEffect(blur)

            scene.addItem(item)

            expanded_size = pixmap.size()
            expanded_size.setWidth(
                expanded_size.width() + padding * 2
            )
            expanded_size.setHeight(
                expanded_size.height() + padding * 2
            )

            expanded = QPixmap(expanded_size)
            expanded.fill(Qt.transparent)

            painter = QPainter(expanded)

            scene.render(
                painter,
                QRectF(0, 0, expanded.width(), expanded.height()),
                QRectF(0, 0, expanded.width(), expanded.height())
            )

            painter.end()

            pixmap = expanded.copy(
                padding,
                padding,
                pixmap.width(),
                pixmap.height()
            )

        # Затемнение
        if self.darkness > 0:
            painter = QPainter(pixmap)

            painter.fillRect(
                pixmap.rect(),
                QColor(0, 0, 0, min(220, self.darkness))
            )

            painter.end()

        return pixmap