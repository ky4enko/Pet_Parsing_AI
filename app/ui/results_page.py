from app.localization import tr
from qfluentwidgets import CardWidget, PrimaryPushButton
from PySide6.QtCore import QUrl
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
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (
    QDesktopServices,
    QPixmap,
    QColor,
    QPainter,
    QPen,
)

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.setFixedSize(22, 22)
        self.hide()

    def start(self):
        self.timer.start(40)
        self.show()

    def stop(self):
        self.timer.stop()
        self.hide()

    def rotate(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#1689e8"), 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        rect = self.rect().adjusted(3, 3, -3, -3)
        painter.drawArc(
            rect,
            self.angle * 16,
            250 * 16,)

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
        status_layout = QHBoxLayout()
        status_layout.setSpacing(8)
        self.loading_spinner = LoadingSpinner(self)
        self.status_label = QLabel(
            "Здесь появятся результаты поиска AUTO.RIA")
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.loading_spinner)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        main_layout.addLayout(status_layout)

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
        """Создаёт карточку автомобиля из JSON-словаря Backend."""

        if not isinstance(car, dict):
            raise TypeError(
                "Backend вернул автомобиль в неожиданном формате: "
                f"{type(car).__name__}")

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

        make = car.get("make") or ""
        model = car.get("model") or ""
        title_text = f"{make} {model}".strip() or tr("Автомобиль")

        title = QLabel(title_text)
        title.setObjectName("carTitle")

        year = car.get("year")
        mileage = car.get("mileage_km")

        details_parts = [
            tr("Год: ") + str(year if year is not None else "—"),
            tr("Пробег: ") + (
                f"{mileage:,} {tr(' км')}"
                if isinstance(mileage, (int, float))
                else (
                    f"{mileage} {tr(' км')}"
                    if mileage is not None else "—")),
        ]

        fuel_name = car.get("fuel_name")
        if fuel_name:
            details_parts.append(tr("Топливо: ") + str(fuel_name))

        modification_name = car.get("modification_name")
        if modification_name:
            details_parts.append(str(modification_name))

        details = QLabel("  •  ".join(details_parts))
        details.setObjectName("carInfo")
        details.setWordWrap(True)

        price_value = car.get("price_usd")
        if isinstance(price_value, (int, float)):
            price_text = f"${price_value:,.0f}"
        else:
            price_text = tr("Цена не указана")

        price = QLabel(price_text)
        price.setObjectName("carPrice")

        open_button = PrimaryPushButton(tr("Открыть объявление"))

        def open_car_url():
            url = str(car.get("url") or "")
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

        photo_url = car.get("photo_url")
        if photo_url:
            photo_url = str(photo_url)
            request = QNetworkRequest(QUrl(photo_url))
            # CDN AUTO.RIA может отклонять запросы без обычного User-Agent/Referer.
            request.setRawHeader(
                b"User-Agent",
                b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",)
            request.setRawHeader(b"Referer", b"https://auto.ria.com/")
            request.setAttribute(
                QNetworkRequest.RedirectPolicyAttribute,
                QNetworkRequest.NoLessSafeRedirectPolicy,)
            reply = self.image_network.get(request)
            self.image_replies.append(reply)

            def set_photo(reply=reply, label=photo_label):
                image_bytes = reply.readAll()
                pixmap = QPixmap()
                loaded = pixmap.loadFromData(image_bytes)

                if loaded and not pixmap.isNull():
                    label.setPixmap(pixmap.scaled(
                        label.size(), Qt.KeepAspectRatio,
                        Qt.SmoothTransformation))
                    label.setText("")
                else:
                    status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
                    label.setText("Фото недоступне")
                    import logging
                    logging.warning(
                        "Не удалось загрузить фото AUTO.RIA: url=%s, http=%s, error=%s",
                        photo_url, status, reply.errorString())
                if reply in self.image_replies:
                    self.image_replies.remove(reply)
                reply.deleteLater()
            reply.finished.connect(set_photo)
        else:
            photo_label.setText("Фото недоступне")
        return card

    def show_loading(self):
        self.clear_cars()
        self.loading_spinner.start()
        self.count_label.setText(tr("Поиск..."))
        self.status_label.setText(
            tr("Выполняется поиск..."))
        self.gpt_text.clear()

    def stop_loading(self):
        self.loading_spinner.stop()

    def update_status(self, message):
        self.status_label.setText(tr(message))

    def show_results(self, result):
        self.stop_loading()
        self.clear_cars()

        cars = result.get("cars") or []
        analysis = result.get("analysis", "")
        analysis_error = result.get("analysis_error")

        total_found = result.get("total_found", len(cars))
        failed_count = result.get("failed_count", 0)

        self.count_label.setText(
            tr("Загружено: ") + str(len(cars)) + tr(" из ") + str(total_found))
        self.status_label.setText(
            tr("Не удалось загрузить: ") + str(failed_count))
        if not cars:
            self.cars_layout.addWidget(
                QLabel(tr("Автомобили не найдены.")))
        else:
            for car in cars:
                self.cars_layout.addWidget(
                    self.create_car_card(car))
        if analysis:
            self.gpt_text.setPlainText(analysis)
        elif analysis_error:
            self.gpt_text.setPlainText(
                tr("Не удалось выполнить анализ GPT.\n\n")
                + analysis_error)
        else:
            self.gpt_text.setPlainText(
                tr("Нет данных для анализа."))