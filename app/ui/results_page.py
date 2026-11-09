from app.localization import tr
from PySide6.QtCore import Qt
from qfluentwidgets import CardWidget, PrimaryPushButton
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QTextBrowser,
    QScrollArea,
)


class ResultsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("resultsPage")
        self.image_network = QNetworkAccessManager(self)
        self.image_replies = []

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(18)

        # Заголовок
        header = QHBoxLayout()

        title = QLabel("Результаты поиска")
        title.setObjectName("pageTitle")

        self.count_label = QLabel("Ожидание результатов")
        self.count_label.setObjectName("countLabel")

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.count_label)

        main_layout.addLayout(header)

        # Статус
        self.status_label = QLabel(
            "Здесь появятся результаты поиска AUTO.RIA"
        )
        self.status_label.setObjectName("statusLabel")

        main_layout.addWidget(self.status_label)

        # Основная область: объявления + GPT
        content_layout = QHBoxLayout()
        content_layout.setSpacing(18)

        # Левая часть — автомобили
        cars_container = QFrame()
        cars_container.setObjectName("contentCard")

        cars_layout = QVBoxLayout(cars_container)
        cars_layout.setContentsMargins(15, 15, 15, 15)

        cars_title = QLabel("Найденные автомобили")
        cars_title.setObjectName("sectionTitle")

        cars_layout.addWidget(cars_title)

        self.cars_scroll = QScrollArea()
        self.cars_scroll.setWidgetResizable(True)
        self.cars_scroll.setFrameShape(QFrame.NoFrame)

        self.cars_widget = QWidget()

        self.cars_layout = QVBoxLayout(self.cars_widget)
        self.cars_layout.setSpacing(12)
        self.cars_layout.setAlignment(Qt.AlignTop)

        self.cars_scroll.setWidget(self.cars_widget)

        cars_layout.addWidget(self.cars_scroll)

        # Правая часть — GPT
        gpt_container = QFrame()
        gpt_container.setObjectName("contentCard")

        gpt_layout = QVBoxLayout(gpt_container)
        gpt_layout.setContentsMargins(15, 15, 15, 15)

        gpt_title = QLabel("Анализ рынка от GPT")
        gpt_title.setObjectName("sectionTitle")

        gpt_layout.addWidget(gpt_title)

        self.gpt_text = QTextBrowser()
        self.gpt_text.setOpenExternalLinks(False)

        self.gpt_text.anchorClicked.connect(
            QDesktopServices.openUrl
        )

        self.gpt_text.setPlaceholderText(
            "Здесь появится аналитика GPT после завершения поиска."
        )

        gpt_layout.addWidget(self.gpt_text)

        content_layout.addWidget(cars_container, 5)
        content_layout.addWidget(gpt_container, 6)

        main_layout.addLayout(content_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget#resultsPage {
                background-color: #202020;
            }

            QLabel#pageTitle {
                color: white;
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#countLabel {
                color: #1689e8;
                font-size: 14px;
                font-weight: 600;
            }

            QLabel#statusLabel {
                color: #aaaaaa;
                font-size: 13px;
            }

            QFrame#contentCard {
                background-color: #292929;
                border: 1px solid #3b3b3b;
                border-radius: 14px;
            }

            QLabel#sectionTitle {
                color: white;
                font-size: 17px;
                font-weight: 600;
            }

            QScrollArea {
                background-color: transparent;
                border: none;
            }

            QTextBrowser {
                background-color: #242424;
                color: #eeeeee;
                border: none;
                border-radius: 8px;
                padding: 14px;
                font-size: 17px;
            }

            QFrame#carCard {
                background-color: #353535;
                border: 1px solid #454545;
                border-radius: 10px;
            }

            QLabel#carPhoto {
                background-color: #20232b;
                border: 1px solid #454545;
                border-radius: 9px;
            }

            QLabel#carTitle {
                color: white;
                font-size: 15px;
                font-weight: 600;
            }

            QLabel#carInfo {
                color: #aaaaaa;
                font-size: 12px;
            }

            QLabel#carPrice {
                color: #36b77b;
                font-size: 19px;
                font-weight: 700;
            }

            QPushButton#linkButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
            }

            QPushButton#linkButton:hover {
                background-color: #1689e8;
            }
        """)

    def clear_cars(self):
        while self.cars_layout.count():
            item = self.cars_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def create_car_card(self, car):
        card = CardWidget(self)
        card.setObjectName("carCard")
        card.setMinimumHeight(132)

        outer_layout = QHBoxLayout(card)
        outer_layout.setContentsMargins(12, 10, 12, 10)
        outer_layout.setSpacing(14)

        photo_label = QLabel()
        photo_label.setObjectName("carPhoto")
        photo_label.setFixedSize(150, 108)
        photo_label.setAlignment(Qt.AlignCenter)
        photo_label.setText("AUTO.RIA")
        outer_layout.addWidget(photo_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        title = QLabel(f"{car.make} {car.model}")
        title.setObjectName("carTitle")

        details_parts = [
            tr("Год: ") + str(car.year if car.year is not None else "—"),
            tr("Пробег: ") + (
                f"{car.mileage_km:,} {tr(' км')}"
                if car.mileage_km is not None else "—"
            ),
        ]
        if getattr(car, "fuel_name", None):
            details_parts.append(tr("Топливо: ") + str(car.fuel_name))
        if getattr(car, "modification_name", None):
            details_parts.append(str(car.modification_name))

        details = QLabel("  •  ".join(details_parts))
        details.setObjectName("carInfo")
        details.setWordWrap(True)

        price_value = car.price_usd
        price_text = f"${price_value:,.0f}" if price_value is not None else tr("Цена не указана")
        price = QLabel(price_text)
        price.setObjectName("carPrice")

        open_button = PrimaryPushButton(tr("Открыть объявление"))

        def open_car_url():
            url = car.url or ""
            if url.startswith("/"):
                url = "https://auto.ria.com" + url
            if url:
                QDesktopServices.openUrl(QUrl(url))

        open_button.clicked.connect(open_car_url)
        info_layout.addWidget(title)
        info_layout.addWidget(details)
        info_layout.addWidget(price)
        info_layout.addWidget(open_button, 0, Qt.AlignLeft)
        outer_layout.addLayout(info_layout, 1)

        photo_url = getattr(car, "photo_url", None)
        if photo_url:
            request = QNetworkRequest(QUrl(photo_url))
            # CDN AUTO.RIA может отклонять запросы без обычного User-Agent/Referer.
            request.setRawHeader(
                b"User-Agent",
                b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            )
            request.setRawHeader(b"Referer", b"https://auto.ria.com/")
            request.setAttribute(
                QNetworkRequest.RedirectPolicyAttribute,
                QNetworkRequest.NoLessSafeRedirectPolicy,
            )
            reply = self.image_network.get(request)
            self.image_replies.append(reply)

            def set_photo(reply=reply, label=photo_label):
                image_bytes = reply.readAll()
                pixmap = QPixmap()
                loaded = pixmap.loadFromData(image_bytes)

                if loaded and not pixmap.isNull():
                    label.setPixmap(pixmap.scaled(
                        label.size(), Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    ))
                    label.setText("")
                else:
                    status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
                    label.setText("Фото недоступне")
                    import logging
                    logging.warning(
                        "Не удалось загрузить фото AUTO.RIA: url=%s, http=%s, error=%s",
                        photo_url, status, reply.errorString()
                    )

                if reply in self.image_replies:
                    self.image_replies.remove(reply)
                reply.deleteLater()

            reply.finished.connect(set_photo)
        else:
            photo_label.setText("Фото недоступне")

        return card

    def show_loading(self):
        self.clear_cars()

        self.count_label.setText(tr("Поиск..."))
        self.status_label.setText(
            tr("Выполняется поиск автомобилей и анализ рынка...")
        )

        self.gpt_text.clear()

    def update_status(self, message):
        self.status_label.setText(tr(message))

    def show_results(self, result):
        self.clear_cars()

        cars = result.get("cars", [])
        analysis = result.get("analysis", "")
        analysis_error = result.get("analysis_error")

        total_found = result.get("total_found", len(cars))
        failed_count = result.get("failed_count", 0)

        self.count_label.setText(
            tr("Загружено: ") + str(len(cars)) + tr(" из ") + str(total_found)
        )

        self.status_label.setText(
            tr("Не удалось загрузить: ") + str(failed_count)
        )

        if not cars:
            self.cars_layout.addWidget(
                QLabel(tr("Автомобили не найдены."))
            )
        else:
            for car in cars:
                self.cars_layout.addWidget(
                    self.create_car_card(car)
                )

        if analysis:
            self.gpt_text.setPlainText(analysis)

        elif analysis_error:
            self.gpt_text.setPlainText(
                tr("Не удалось выполнить анализ GPT.\n\n")
                + analysis_error
            )

        else:
            self.gpt_text.setPlainText(
                tr("Нет данных для анализа.")
            )