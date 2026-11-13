import logging
from app.localization import tr
from qfluentwidgets import PrimaryPushButton
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import (
    QDesktopServices,
    QPixmap,
    QColor,
    QPainter,
    QPen,
)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QTextBrowser,
    QScrollArea,
)

class LoadingSpinner(QWidget):
    """Компактный индикатор выполнения поиска."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.setFixedSize(24, 24)
        self.hide()

    def start(self):
        self.angle = 0
        self.timer.start(40)
        self.show()
        self.update()

    def stop(self):
        self.timer.stop()
        self.hide()

    def rotate(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#FF9B35"), 2.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        rect = self.rect().adjusted(3, 3, -3, -3)
        painter.drawArc(rect, self.angle * 16, 255 * 16)


class ResultsPage(QWidget):
    """Страница результатов поиска и анализа рынка."""

    def __init__(self):
        super().__init__()

        self.setObjectName("resultsPage")
        self.image_network = QNetworkAccessManager(self)
        self.image_replies = []

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(16)

        # Заголовок страницы
        header = QHBoxLayout()
        header.setSpacing(12)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel("Результаты поиска")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Объявления AUTO.RIA и аналитика рыночной стоимости")
        subtitle.setObjectName("pageSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        self.count_label = QLabel("Ожидание результатов")
        self.count_label.setObjectName("countLabel")
        self.count_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        header.addLayout(title_layout)
        header.addStretch(1)
        header.addWidget(self.count_label)
        main_layout.addLayout(header)

        # Статус выполнения: spinner во время поиска, галочка после ответа.
        self.status_card = QFrame()
        self.status_card.setObjectName("statusCard")

        status_layout = QHBoxLayout(self.status_card)
        status_layout.setContentsMargins(14, 10, 14, 10)
        status_layout.setSpacing(10)

        self.loading_spinner = LoadingSpinner(self.status_card)

        self.completion_icon = QLabel("✓")
        self.completion_icon.setObjectName("completionIcon")
        self.completion_icon.setFixedSize(24, 24)
        self.completion_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.completion_icon.hide()

        self.status_label = QLabel(
            "Здесь появятся результаты поиска AUTO.RIA"
        )
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)

        status_layout.addWidget(self.loading_spinner)
        status_layout.addWidget(self.completion_icon)
        status_layout.addWidget(self.status_label, 1)
        main_layout.addWidget(self.status_card)

        # Карточки со сводными показателями
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(12)

        self.loaded_value = self._add_metric(
            metrics_layout,
            "Загружено автомобилей",
            "—",
        )
        self.total_value = self._add_metric(
            metrics_layout,
            "Найдено объявлений",
            "—",
        )
        self.failed_value = self._add_metric(
            metrics_layout,
            "Не удалось загрузить",
            "—",
        )

        main_layout.addLayout(metrics_layout)

        # Основной контент: объявления и GPT-анализ
        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        # Левая панель — автомобили
        cars_container = QFrame()
        cars_container.setObjectName("contentPanel")

        cars_layout = QVBoxLayout(cars_container)
        cars_layout.setContentsMargins(16, 16, 16, 16)
        cars_layout.setSpacing(12)

        cars_header = QHBoxLayout()
        cars_title = QLabel("Найденные автомобили")
        cars_title.setObjectName("sectionTitle")

        self.cars_count_badge = QLabel("0")
        self.cars_count_badge.setObjectName("sectionBadge")

        cars_header.addWidget(cars_title)
        cars_header.addStretch(1)
        cars_header.addWidget(self.cars_count_badge)
        cars_layout.addLayout(cars_header)

        self.cars_scroll = QScrollArea()
        self.cars_scroll.setWidgetResizable(True)
        self.cars_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.cars_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.cars_widget = QWidget()
        self.cars_layout = QVBoxLayout(self.cars_widget)
        self.cars_layout.setContentsMargins(2, 2, 6, 2)
        self.cars_layout.setSpacing(11)
        self.cars_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.cars_scroll.setWidget(self.cars_widget)
        cars_layout.addWidget(self.cars_scroll, 1)

        # Правая панель — GPT
        gpt_container = QFrame()
        gpt_container.setObjectName("contentPanel")

        gpt_layout = QVBoxLayout(gpt_container)
        gpt_layout.setContentsMargins(16, 16, 16, 16)
        gpt_layout.setSpacing(12)

        gpt_header = QVBoxLayout()
        gpt_header.setSpacing(3)

        gpt_title = QLabel("Анализ рынка от GPT")
        gpt_title.setObjectName("sectionTitle")

        gpt_subtitle = QLabel(
            "Оценка цен, сравнение объявлений и выводы"
        )
        gpt_subtitle.setObjectName("panelSubtitle")

        gpt_header.addWidget(gpt_title)
        gpt_header.addWidget(gpt_subtitle)
        gpt_layout.addLayout(gpt_header)

        self.gpt_text = QTextBrowser()
        self.gpt_text.setObjectName("gptText")
        self.gpt_text.setOpenExternalLinks(False)
        self.gpt_text.anchorClicked.connect(
            QDesktopServices.openUrl
        )
        self.gpt_text.setPlaceholderText(
            "Здесь появится аналитика GPT после завершения поиска."
        )
        gpt_layout.addWidget(self.gpt_text, 1)

        content_layout.addWidget(cars_container, 6)
        content_layout.addWidget(gpt_container, 5)
        main_layout.addLayout(content_layout, 1)

    def _add_metric(self, layout, caption, initial_value):
        card = QFrame()
        card.setObjectName("metricCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(3)

        caption_label = QLabel(caption)
        caption_label.setObjectName("metricCaption")

        value_label = QLabel(initial_value)
        value_label.setObjectName("metricValue")

        card_layout.addWidget(caption_label)
        card_layout.addWidget(value_label)

        layout.addWidget(card, 1)
        return value_label

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget#resultsPage {
                background: transparent;
            }

            QLabel {
                background: transparent;
            }

            QLabel#pageTitle {
                color: white;
                font-size: 27px;
                font-weight: 800;
            }

            QLabel#pageSubtitle,
            QLabel#panelSubtitle {
                color: rgba(225, 229, 238, 155);
                font-size: 12px;
            }

            QLabel#countLabel {
                color: #FFB45F;
                background-color: rgba(255, 145, 55, 28);
                border: 1px solid rgba(255, 155, 53, 110);
                border-radius: 10px;
                padding: 8px 13px;
                font-size: 12px;
                font-weight: 700;
            }

            QFrame#statusCard,
            QFrame#metricCard,
            QFrame#contentPanel {
                background-color: rgba(17, 19, 29, 218);
                border: 1px solid rgba(255, 145, 55, 72);
                border-radius: 14px;
            }

            QLabel#statusLabel {
                color: rgba(245, 245, 248, 225);
                font-size: 13px;
            }

            QLabel#completionIcon {
                color: #42D392;
                font-size: 23px;
                font-weight: 900;
            }

            QLabel#metricCaption {
                color: rgba(225, 229, 238, 155);
                font-size: 11px;
            }

            QLabel#metricValue {
                color: white;
                font-size: 22px;
                font-weight: 800;
            }

            QLabel#sectionTitle {
                color: white;
                font-size: 16px;
                font-weight: 750;
            }

            QLabel#sectionBadge {
                color: #FFB45F;
                background-color: rgba(255, 145, 55, 35);
                border: 1px solid rgba(255, 155, 53, 90);
                border-radius: 9px;
                min-width: 28px;
                padding: 4px 7px;
                font-size: 11px;
                font-weight: 700;
            }

            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollArea QWidget {
                background: transparent;
            }

            QTextBrowser#gptText {
                background-color: rgba(10, 12, 19, 175);
                color: #ECEEF3;
                border: 1px solid rgba(255, 255, 255, 24);
                border-radius: 10px;
                padding: 12px;
                font-size: 15px;
                selection-background-color: rgba(255, 145, 55, 110);
            }

            QFrame#carCard {
                background-color: rgba(35, 38, 49, 238);
                border: 1px solid rgba(255, 255, 255, 34);
                border-radius: 12px;
            }

            QFrame#carCard:hover {
                border: 1px solid rgba(255, 155, 53, 170);
                background-color: rgba(43, 43, 52, 245);
            }

            QLabel#carPhoto {
                color: rgba(235, 235, 240, 145);
                background-color: rgba(12, 15, 23, 220);
                border: 1px solid rgba(255, 255, 255, 35);
                border-radius: 9px;
                font-size: 11px;
            }

            QLabel#carTitle {
                color: white;
                font-size: 15px;
                font-weight: 750;
            }

            QLabel#carDetails {
                color: rgba(225, 229, 238, 180);
                font-size: 11px;
            }

            QLabel#carPrice {
                color: #54D69A;
                font-size: 20px;
                font-weight: 850;
            }

            QLabel#carPriceSecondary {
                color: rgba(225, 229, 238, 145);
                font-size: 11px;
            }

            QPushButton#openListingButton {
                font-size: 11px;
                font-weight: 650;
                padding: 6px 12px;
            }

            QScrollBar:vertical {
                background: rgba(255, 255, 255, 12);
                width: 8px;
                margin: 3px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical {
                background: rgba(255, 155, 53, 115);
                min-height: 28px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical:hover {
                background: rgba(255, 175, 85, 190);
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

    @staticmethod
    def _format_number(value):
        if value is None:
            return "—"
        if isinstance(value, (int, float)):
            return f"{value:,.0f}".replace(",", " ")
        return str(value)

    def _format_car_details(self, car):
        details = []

        year = car.get("year")
        if year is not None:
            details.append(f"{tr('Год')}: {year}")

        mileage = car.get("mileage_km")
        if mileage is not None:
            details.append(
                f"{tr('Пробег')}: {self._format_number(mileage)} {tr('км')}"
            )

        fuel = car.get("fuel_name")
        if fuel:
            details.append(str(fuel))

        engine = car.get("engine_volume_l")
        if engine is not None:
            details.append(f"{self._format_number(engine)} {tr('л')}")

        gearbox = car.get("gearbox")
        if gearbox:
            details.append(str(gearbox))

        drive = car.get("drive_type")
        if drive:
            details.append(str(drive))

        modification = car.get("modification_name")
        if modification:
            details.append(str(modification))

        return "  •  ".join(details) if details else tr("Характеристики не указаны")

    def _clear_pending_images(self):
        for reply in list(self.image_replies):
            try:
                reply.finished.disconnect()
            except (RuntimeError, TypeError):
                pass
            reply.abort()
            reply.deleteLater()
        self.image_replies.clear()

    def clear_cars(self):
        self._clear_pending_images()

        while self.cars_layout.count():
            item = self.cars_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _add_empty_state(self, title, description):
        empty = QFrame()
        empty.setObjectName("emptyState")

        layout = QVBoxLayout(empty)
        layout.setContentsMargins(20, 34, 20, 34)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("🚘")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 38px;")

        title_label = QLabel(title)
        title_label.setObjectName("emptyTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description_label = QLabel(description)
        description_label.setObjectName("emptyDescription")
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon)
        layout.addWidget(title_label)
        layout.addWidget(description_label)

        empty.setStyleSheet("""
            QFrame#emptyState {
                background-color: rgba(255, 255, 255, 10);
                border: 1px dashed rgba(255, 255, 255, 45);
                border-radius: 12px;
            }
            QLabel#emptyTitle {
                color: white;
                font-size: 15px;
                font-weight: 700;
            }
            QLabel#emptyDescription {
                color: rgba(225, 229, 238, 155);
                font-size: 12px;
            }
        """)
        self.cars_layout.addWidget(empty)

    def create_car_card(self, car):
        """Создаёт карточку объявления из JSON-словаря Backend."""
        if not isinstance(car, dict):
            raise TypeError(
                "Сервер вернул автомобиль в неожиданном формате: "
                f"{type(car).__name__}"
            )

        card = QFrame(self.cars_widget)
        card.setObjectName("carCard")
        card.setMinimumHeight(142)

        outer_layout = QHBoxLayout(card)
        outer_layout.setContentsMargins(11, 11, 11, 11)
        outer_layout.setSpacing(13)

        photo_label = QLabel(tr("Фото AUTO.RIA"))
        photo_label.setObjectName("carPhoto")
        photo_label.setFixedSize(154, 116)
        photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_label.setWordWrap(True)
        outer_layout.addWidget(photo_label)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 1, 0, 1)
        info_layout.setSpacing(5)

        make = str(car.get("make") or "").strip()
        model = str(car.get("model") or "").strip()
        title_text = f"{make} {model}".strip() or tr("Автомобиль")

        title = QLabel(title_text)
        title.setObjectName("carTitle")
        title.setWordWrap(True)

        details = QLabel(self._format_car_details(car))
        details.setObjectName("carDetails")
        details.setWordWrap(True)

        price_usd = car.get("price_usd")
        price_uah = car.get("price_uah")

        if price_usd is not None:
            price_text = f"${self._format_number(price_usd)}"
        elif price_uah is not None:
            price_text = f"{self._format_number(price_uah)} ₴"
        else:
            price_text = tr("Цена не указана")

        price = QLabel(price_text)
        price.setObjectName("carPrice")

        info_layout.addWidget(title)
        info_layout.addWidget(details)
        info_layout.addWidget(price)

        if price_usd is not None and price_uah is not None:
            secondary_price = QLabel(
                f"{self._format_number(price_uah)} ₴"
            )
            secondary_price.setObjectName("carPriceSecondary")
            info_layout.addWidget(secondary_price)

        open_button = PrimaryPushButton(tr("Открыть объявление"))
        open_button.setObjectName("openListingButton")
        open_button.setCursor(Qt.CursorShape.PointingHandCursor)

        def open_car_url():
            url = str(car.get("url") or "").strip()
            if url.startswith("/"):
                url = "https://auto.ria.com" + url
            if url:
                QDesktopServices.openUrl(QUrl(url))

        open_button.clicked.connect(open_car_url)
        info_layout.addWidget(open_button, 0, Qt.AlignmentFlag.AlignLeft)
        outer_layout.addLayout(info_layout, 1)

        photo_url = car.get("photo_url")
        if photo_url:
            request = QNetworkRequest(QUrl(str(photo_url)))
            request.setRawHeader(
                b"User-Agent",
                b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                b"AppleWebKit/537.36 Chrome/120 Safari/537.36",
            )
            request.setRawHeader(b"Referer", b"https://auto.ria.com/")
            request.setAttribute(
                QNetworkRequest.Attribute.RedirectPolicyAttribute,
                QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy,
            )

            reply = self.image_network.get(request)
            self.image_replies.append(reply)

            def set_photo(reply=reply, label=photo_label):
                if reply.error() == QNetworkReply.NetworkError.NoError:
                    image_bytes = reply.readAll()
                    pixmap = QPixmap()
                    if pixmap.loadFromData(image_bytes) and not pixmap.isNull():
                        label.setPixmap(
                            pixmap.scaled(
                                label.size(),
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation,
                            )
                        )
                        label.setText("")
                    else:
                        label.setText(tr("Фото недоступно"))
                else:
                    status = reply.attribute(
                        QNetworkRequest.Attribute.HttpStatusCodeAttribute
                    )
                    logging.warning(
                        "Не удалось загрузить фото AUTO.RIA: url=%s, http=%s, error=%s",
                        photo_url,
                        status,
                        reply.errorString(),
                    )
                    label.setText(tr("Фото недоступно"))

                if reply in self.image_replies:
                    self.image_replies.remove(reply)
                reply.deleteLater()

            reply.finished.connect(set_photo)

        return card

    def show_loading(self):
        self.clear_cars()
        self.loading_spinner.start()
        self.completion_icon.hide()
        self.completion_icon.setText("✓")
        self.completion_icon.setStyleSheet("")
        self.count_label.setText(tr("Поиск выполняется"))
        self.status_label.setText(tr("Выполняется поиск..."))

        self.loaded_value.setText("—")
        self.total_value.setText("—")
        self.failed_value.setText("—")
        self.cars_count_badge.setText("0")
        self.gpt_text.clear()

    def stop_loading(self):
        self.loading_spinner.stop()

    def update_status(self, message):
        self.status_label.setText(tr(message))

    def show_error(self, error):
        self.loading_spinner.stop()
        self.completion_icon.setText("!")
        self.completion_icon.setStyleSheet(
            "color: #FF6B6B; font-size: 22px; font-weight: 900;"
        )
        self.completion_icon.show()
        self.count_label.setText(tr("Ошибка поиска"))
        self.status_label.setText(tr("Не удалось завершить поиск. Подробности в сообщении об ошибке."))
        self.gpt_text.setPlainText(str(error))

    def show_results(self, result):
        self.loading_spinner.stop()
        self.completion_icon.setStyleSheet("")
        self.clear_cars()

        if not isinstance(result, dict):
            self.show_error(
                f"Сервер вернул неожиданный формат ответа: {type(result).__name__}"
            )
            return

        cars = result.get("cars") or []
        if not isinstance(cars, list):
            cars = []

        analysis = result.get("analysis") or ""
        analysis_error = result.get("analysis_error")
        status = result.get("status", "completed")
        is_history = bool(result.get("is_history"))

        total_found = result.get("total_found")
        failed_count = result.get("failed_count")
        search_id = result.get("search_id")

        self.loaded_value.setText(str(len(cars)))
        self.total_value.setText(
            "—" if total_found is None else str(total_found)
        )
        self.failed_value.setText(
            "—" if failed_count is None else str(failed_count)
        )
        self.cars_count_badge.setText(str(len(cars)))

        if search_id is not None:
            self.count_label.setText(f"{tr('Поиск')} #{search_id}")
        else:
            self.count_label.setText(
                f"{tr('Загружено')}: {len(cars)}"
            )

        if status == "failed":
            self.completion_icon.setText("!")
            self.completion_icon.setStyleSheet(
                "color: #FF6B6B; font-size: 22px; font-weight: 900;"
            )
            self.status_label.setText(
                tr("Поиск завершился с ошибкой при загрузке объявлений.")
            )
        else:
            self.completion_icon.setText("✓")
            if is_history:
                self.status_label.setText(
                    tr("Открыты сохранённые результаты поиска.")
                )
            else:
                self.status_label.setText(
                    tr("Поиск завершён.")
                )

        self.completion_icon.show()

        if cars:
            for car in cars:
                self.cars_layout.addWidget(self.create_car_card(car))
        else:
            self._add_empty_state(
                tr("Автомобили не найдены"),
                tr(
                    "Поиск завершён поиск, но подходящих объявлений нет. "
                    "Попробуйте изменить параметры поиска."
                ),
            )

        if analysis:
            self.gpt_text.setMarkdown(str(analysis))
        elif analysis_error:
            self.gpt_text.setPlainText(
                tr("Не удалось выполнить анализ GPT.\n\n")
                + str(analysis_error)
            )
        elif not cars:
            self.gpt_text.setPlainText(
                tr("GPT-анализ не запускался, потому что объявления не найдены.")
            )
        else:
            self.gpt_text.setPlainText(
                tr("Сервер не вернул текст GPT-анализа.")
            )
