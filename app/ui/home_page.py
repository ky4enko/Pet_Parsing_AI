
from pathlib import Path

from app.localization import tr
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)


class HomePage(QWidget):

    combustionRequested = Signal()
    electricRequested = Signal()

    def __init__(self):
        super().__init__()

        self.setObjectName("homePage")
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(38, 30, 38, 24)
        main_layout.setSpacing(15)

        title = QLabel("AUTO.RIA ANALYZER")
        title.setObjectName("pageTitle")
        main_layout.addWidget(title)

        main_layout.addStretch(1)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(28)

        combustion_card = self.create_card(
            icon="car",
            title="ДВС / Гибрид",
            description=(
                "Поиск автомобилей с бензиновыми,\n"
                "дизельными и гибридными двигателями"
            ),
            button_text="Начать поиск",
        )

        electric_card = self.create_card(
            icon="electric",
            title="Электромобили",
            description=(
                "Поиск электромобилей и анализ\n"
                "их рыночной стоимости"
            ),
            button_text="Начать поиск",
        )

        combustion_card["button"].clicked.connect(
            self.combustionRequested.emit
        )

        electric_card["button"].clicked.connect(
            self.electricRequested.emit
        )

        cards_layout.addWidget(combustion_card["frame"], 1)
        cards_layout.addWidget(electric_card["frame"], 1)

        main_layout.addLayout(cards_layout, 5)
        main_layout.addStretch(1)

        footer = QLabel(
            "AUTO.RIA CAR PRICE ANALYZER   •   AI MARKET ANALYSIS"
        )
        footer.setObjectName("footer")
        main_layout.addWidget(footer)

    def create_card(self, icon, title, description, button_text):

        frame = QFrame()
        frame.setObjectName("vehicleCard")

        frame.setMinimumHeight(440)
        frame.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(28, 24, 28, 25)
        layout.setSpacing(12)

        # Область изображения — одинаковая для обеих карточек
        icon_container = QWidget()
        icon_container.setFixedHeight(220)

        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)

        if icon == "car":
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignCenter)

            image_path = (
                Path(__file__).resolve().parent
                / "assets"
                / "muscle_car.png"
            )

            pixmap = QPixmap(str(image_path))

            if not pixmap.isNull():
                icon_label.setPixmap(
                    pixmap.scaled(
                        250,
                        125,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
            else:
                icon_label.setText(tr("Изображение muscle_car.png не найдено"))
                icon_label.setStyleSheet("color: #FF9B35;")

            icon_layout.addWidget(icon_label)

        else:
            icon_label = QLabel("⚡")
            icon_label.setAlignment(Qt.AlignCenter)

            font = QFont()
            font.setPointSize(95)
            icon_label.setFont(font)

            icon_layout.addWidget(icon_label)

        layout.addWidget(icon_container)

        # Заголовок
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Описание
        description_label = QLabel(description)
        description_label.setObjectName("cardDescription")
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        layout.addStretch(1)

        # Кнопка
        button = QPushButton(button_text)
        button.setObjectName("primaryButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(66)

        font = QFont()
        font.setPointSize(17)
        font.setBold(True)
        button.setFont(font)

        layout.addWidget(button)

        # Одинаковое оранжевое свечение для обеих карточек
        shadow = QGraphicsDropShadowEffect(frame)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(255, 105, 25, 55))

        frame.setGraphicsEffect(shadow)

        return {
            "frame": frame,
            "button": button,
        }

    def apply_styles(self):

        self.setStyleSheet("""
            QWidget#homePage {
                background: transparent;
            }

            QLabel#pageTitle {
                color: white;
                font-size: 32px;
                font-weight: 800;
                background: transparent;
                padding: 5px 3px;
            }

            QFrame#vehicleCard {
                background-color: rgba(17, 19, 29, 175);
                border: 1px solid rgba(255, 135, 45, 145);
                border-radius: 27px;
            }

            QFrame#vehicleCard:hover {
                background-color: rgba(27, 22, 27, 205);
                border: 1px solid #FF9B35;
            }

            QLabel#cardTitle {
                color: white;
                font-size: 29px;
                font-weight: 800;
                background: transparent;
                padding: 3px;
            }

            QLabel#cardDescription {
                color: rgba(255, 255, 255, 235);
                font-size: 17px;
                background: transparent;
                padding: 3px;
            }

            QPushButton#primaryButton {
                color: white;
                background-color: rgba(255, 104, 25, 45);
                border: 2px solid #FF9B35;
                border-radius: 17px;
                padding: 10px 18px;
            }

            QPushButton#primaryButton:hover {
                background-color: rgba(255, 111, 25, 115);
                border: 2px solid #FFD071;
            }

            QPushButton#primaryButton:pressed {
                background-color: rgba(255, 75, 15, 175);
                border: 2px solid white;
            }

            QLabel#footer {
                color: rgba(255, 255, 255, 190);
                font-size: 12px;
                background: transparent;
                padding: 4px;
            }
        """)
