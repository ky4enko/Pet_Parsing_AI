from app.localization import tr
from PySide6.QtGui import QPixmap, QImageReader
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QSlider,
    QFrame,
    QWidget,
)


class ThemeDialog(QDialog):

    themeChanged = Signal()

    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)

        self.theme_manager = theme_manager

        # Кэш загруженных изображений
        self.image_cache = {}

        self.theme_buttons = {}

        self.setWindowTitle("Персонализация")
        self.resize(1050, 780)
        self.setMinimumSize(850, 650)

        # Предварительно загружаем изображения
        self.preload_images()

        self.init_ui()
        self.apply_styles()
        self.update_preview()
        self.update_selection()

    def preload_images(self):
        """Загружает все изображения в память заранее."""

        for number, theme in self.theme_manager.get_themes().items():
            reader = QImageReader(str(theme["path"]))
            reader.setAutoTransform(True)

            image = reader.read()
            pixmap = QPixmap.fromImage(image) if not image.isNull() else QPixmap()

            if not pixmap.isNull():
                self.image_cache[number] = pixmap

        print(
            f"Загружено превью: {len(self.image_cache)}"
        )

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(18)

        title = QLabel("Персонализация")
        title.setObjectName("mainTitle")

        subtitle = QLabel(
            "Выберите оформление приложения"
        )
        subtitle.setObjectName("subtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # Основная область
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)

        # Левая часть — большое превью
        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)

        preview_title = QLabel("Предпросмотр")
        preview_title.setObjectName("sectionTitle")

        self.large_preview = QLabel()
        self.large_preview.setObjectName("largePreview")
        self.large_preview.setFixedSize(420, 270)
        self.large_preview.setAlignment(Qt.AlignCenter)

        self.selected_name = QLabel()
        self.selected_name.setObjectName("selectedName")

        left_layout.addWidget(preview_title)
        left_layout.addWidget(self.large_preview)
        left_layout.addWidget(self.selected_name)
        left_layout.addStretch()

        # Правая часть — миниатюры
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)

        themes_title = QLabel("Выберите тему для применения")
        themes_title.setObjectName("sectionTitle")

        right_layout.addWidget(themes_title)

        grid = QGridLayout()
        grid.setSpacing(12)

        themes = self.theme_manager.get_themes()

        if not themes:
            error = QLabel(
                "Изображения не найдены.\n"
                "Проверьте папку assets/backgrounds."
            )
            error.setObjectName("errorLabel")
            error.setWordWrap(True)
            grid.addWidget(error, 0, 0)

        for index, (number, theme) in enumerate(themes.items()):

            card = QFrame()
            card.setObjectName("thumbnailCard")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(5, 5, 5, 5)
            card_layout.setSpacing(5)

            thumbnail = QLabel()
            thumbnail.setFixedSize(135, 95)
            thumbnail.setAlignment(Qt.AlignCenter)

            pixmap = self.image_cache.get(number)

            if pixmap:
                thumbnail.setPixmap(
                    pixmap.scaled(
                        thumbnail.size(),
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                )

            button = QPushButton(
                f"Стиль {number}"
            )

            button.setCursor(Qt.PointingHandCursor)

            button.clicked.connect(
                lambda checked=False, n=number:
                self.select_theme(n)
            )

            card_layout.addWidget(thumbnail)
            card_layout.addWidget(button)

            row = index // 3
            column = index % 3

            grid.addWidget(card, row, column)

            self.theme_buttons[number] = button

        right_layout.addLayout(grid)
        right_layout.addStretch()

        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 1)

        main_layout.addLayout(content_layout, 1)

        # Настройки размытия
        blur_title = QLabel("Размытие фона")
        blur_title.setObjectName("sectionTitle")

        self.blur_value = QLabel(
            str(self.theme_manager.blur_radius)
        )

        blur_layout = QHBoxLayout()
        blur_layout.addWidget(blur_title)
        blur_layout.addStretch()
        blur_layout.addWidget(self.blur_value)

        self.blur_slider = QSlider(Qt.Horizontal)
        self.blur_slider.setRange(0, 40)
        self.blur_slider.setValue(
            self.theme_manager.blur_radius
        )
        self.blur_slider.valueChanged.connect(
            self.change_blur
        )

        main_layout.addLayout(blur_layout)
        main_layout.addWidget(self.blur_slider)

        # Настройки затемнения
        darkness_title = QLabel("Затемнение фона")
        darkness_title.setObjectName("sectionTitle")

        self.darkness_value = QLabel(
            str(self.theme_manager.get_darkness())
        )

        darkness_layout = QHBoxLayout()
        darkness_layout.addWidget(darkness_title)
        darkness_layout.addStretch()
        darkness_layout.addWidget(self.darkness_value)

        self.darkness_slider = QSlider(Qt.Horizontal)
        self.darkness_slider.setRange(0, 220)
        self.darkness_slider.setValue(
            self.theme_manager.get_darkness()
        )
        self.darkness_slider.valueChanged.connect(
            self.change_darkness
        )

        main_layout.addLayout(darkness_layout)
        main_layout.addWidget(self.darkness_slider)

        # Кнопка закрытия
        close_button = QPushButton("Готово")
        close_button.setObjectName("closeButton")
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.accept)

        main_layout.addSpacing(8)
        main_layout.addWidget(close_button)

    def select_theme(self, number):
        if self.theme_manager.set_theme(number):
            self.update_preview()
            self.update_selection()
            self.themeChanged.emit()

    def update_preview(self):
        number = self.theme_manager.current_theme

        pixmap = self.image_cache.get(number)

        if pixmap:
            self.large_preview.setPixmap(
                pixmap.scaled(
                    self.large_preview.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )

            self.selected_name.setText(
                tr("Выбрано: Стиль ") + str(number)
            )

        else:
            self.large_preview.setText(
                tr("Нет изображения")
            )

    def update_selection(self):
        for number, button in self.theme_buttons.items():

            if number == self.theme_manager.current_theme:
                button.setText(tr("✓ Выбрано"))
                button.setProperty("selected", True)
            else:
                button.setText(tr("Стиль ") + str(number))
                button.setProperty("selected", False)

            button.style().unpolish(button)
            button.style().polish(button)

    def change_blur(self, value):
        self.theme_manager.set_blur(value)
        self.blur_value.setText(str(value))
        self.themeChanged.emit()

    def change_darkness(self, value):
        self.theme_manager.set_darkness(value)
        self.darkness_value.setText(str(value))
        self.themeChanged.emit()

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1b202d;
                color: white;
            }

            QLabel {
                color: white;
                background: transparent;
            }

            QLabel#mainTitle {
                font-size: 30px;
                font-weight: bold;
            }

            QLabel#subtitle {
                font-size: 15px;
                color: #aeb7c9;
            }

            QLabel#sectionTitle {
                font-size: 15px;
                font-weight: bold;
            }

            QLabel#largePreview {
                background-color: #111722;
                border: 3px solid #080b12;
                border-radius: 16px;
            }

            QLabel#selectedName {
                font-size: 14px;
                color: #b8c5dc;
            }

            QFrame#thumbnailCard {
                background-color: #252c3b;
                border: 2px solid transparent;
                border-radius: 10px;
            }

            QFrame#thumbnailCard:hover {
                border: 2px solid #1689e8;
            }

            QPushButton {
                background-color: #30394c;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #3c4d6c;
            }

            QPushButton[selected="true"] {
                background-color: #0878d1;
                border: 1px solid #45aaff;
            }

            QPushButton#closeButton {
                background-color: #35415a;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton#closeButton:hover {
                background-color: #0878d1;
            }

            QSlider::groove:horizontal {
                height: 6px;
                background: #414b60;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                background: #1689e8;
                width: 17px;
                margin: -6px 0;
                border-radius: 8px;
            }

            QLabel#errorLabel {
                color: #ff7777;
                font-size: 14px;
            }
        """)
