from datetime import datetime
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from backend_client import BackendClient
from app.localization import tr


class DataLoader(QThread):
    """Выполняет запросы к Backend вне основного потока интерфейса."""

    resultReady = Signal(object)
    errorOccurred = Signal(str)

    def __init__(self, function, *args):
        super().__init__()
        self.function = function
        self.args = args

    def run(self):
        try:
            self.resultReady.emit(self.function(*self.args))
        except Exception as error:
            self.errorOccurred.emit(str(error))


class HistoryPage(QWidget):
    """История поисков из PostgreSQL через существующий Backend API."""

    PAGE_SIZE = 20
    resultRequested = Signal(dict)

    def __init__(self):
        super().__init__()

        self.setObjectName("historyPage")
        self.backend_client = BackendClient()
        self._workers = []
        self._history_items = []
        self._open_buttons = {}
        self._history_loading = False
        self._has_more_history = False
        self._details_loading = False
        self._active_search_id = None
        self._state_key = "loading"
        self._state_detail = ""

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(16)

        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        title_layout.setSpacing(6)

        self.title_label = QLabel(tr("История поисков"))
        self.title_label.setObjectName("pageTitle")

        self.subtitle_label = QLabel(
            tr("Ранее выполненные поиски и сохранённые результаты.")
        )
        self.subtitle_label.setObjectName("pageSubtitle")
        self.subtitle_label.setWordWrap(True)

        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)
        header_layout.addLayout(title_layout, 1)

        self.refresh_button = QPushButton(tr("Обновить"))
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.setMinimumSize(112, 42)
        self.refresh_button.clicked.connect(self.load_history)
        header_layout.addWidget(
            self.refresh_button,
            0,
            Qt.AlignmentFlag.AlignTop
        )

        main_layout.addLayout(header_layout)

        info_layout = QHBoxLayout()
        self.count_label = QLabel(tr("Поисков: 0"))
        self.count_label.setObjectName("historyCount")
        info_layout.addWidget(self.count_label)
        info_layout.addStretch()

        main_layout.addLayout(info_layout)

        self.status_label = QLabel("")
        self.status_label.setObjectName("historyStatus")
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("historyScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.cards_widget = QWidget()
        self.cards_widget.setObjectName("historyCardsWidget")
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setContentsMargins(2, 2, 8, 12)
        self.cards_layout.setSpacing(12)

        self.scroll_area.setWidget(self.cards_widget)
        main_layout.addWidget(self.scroll_area, 1)

        self.load_more_button = QPushButton(tr("Загрузить ещё"))
        self.load_more_button.setObjectName("loadMoreButton")
        self.load_more_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_more_button.setMinimumSize(150, 40)
        self.load_more_button.clicked.connect(self.load_more_history)
        self.load_more_button.hide()
        main_layout.addWidget(
            self.load_more_button,
            0,
            Qt.AlignmentFlag.AlignHCenter
        )

        self.show_state("loading")

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget#historyPage {
                background: transparent;
            }

            QLabel#pageTitle {
                color: white;
                font-size: 30px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#pageSubtitle {
                color: #aaaaaa;
                font-size: 14px;
                background: transparent;
            }

            QLabel#historyCount {
                color: #FFB36B;
                font-size: 13px;
                font-weight: 600;
                background: transparent;
                padding: 3px 1px;
            }

            QLabel#historyStatus {
                color: #aaaaaa;
                font-size: 13px;
                background: transparent;
            }

            QScrollArea#historyScrollArea {
                background: transparent;
                border: none;
            }

            QScrollArea#historyScrollArea QWidget#qt_scrollarea_viewport {
                background: transparent;
            }

            QWidget#historyCardsWidget {
                background: transparent;
            }

            QFrame#historyCard {
                background-color: rgba(17, 19, 29, 190);
                border: 1px solid rgba(255, 135, 45, 85);
                border-radius: 14px;
            }

            QFrame#historyCard:hover {
                background-color: rgba(27, 22, 27, 220);
                border: 1px solid rgba(255, 155, 53, 190);
            }

            QLabel#historyTitle {
                color: #ffffff;
                font-size: 16px;
                font-weight: 700;
                background: transparent;
            }

            QLabel#historyDetails {
                color: #d0d0d0;
                font-size: 13px;
                background: transparent;
            }

            QLabel#historyMeta {
                color: #969696;
                font-size: 11px;
                background: transparent;
            }

            QPushButton#historyOpenButton {
                color: white;
                background-color: rgba(255, 104, 25, 42);
                border: 1px solid #C77A3D;
                border-radius: 9px;
                padding: 8px 14px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#historyOpenButton:hover {
                background-color: rgba(255, 111, 25, 105);
                border: 1px solid #FFD071;
            }

            QPushButton#historyOpenButton:disabled {
                color: #a0a0a0;
                background-color: rgba(80, 80, 80, 90);
                border: 1px solid #555555;
            }

            QPushButton#refreshButton {
                color: white;
                background-color: rgba(255, 104, 25, 35);
                border: 1px solid rgba(255, 155, 53, 175);
                border-radius: 9px;
                padding: 8px 14px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#refreshButton:hover {
                background-color: rgba(255, 111, 25, 100);
                border: 1px solid #FFD071;
            }

            QPushButton#refreshButton:disabled {
                color: #888888;
                background-color: #353535;
                border: 1px solid #505050;
            }

            QPushButton#loadMoreButton {
                color: #f0f0f0;
                background-color: rgba(40, 40, 40, 190);
                border: 1px solid rgba(255, 155, 53, 110);
                border-radius: 9px;
                padding: 7px 18px;
                font-size: 13px;
            }

            QPushButton#loadMoreButton:hover {
                background-color: rgba(255, 111, 25, 65);
                border: 1px solid #FFB36B;
            }

            QPushButton#loadMoreButton:disabled {
                color: #888888;
                background-color: #353535;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: rgba(255, 155, 53, 105);
                border-radius: 4px;
                min-height: 28px;
            }

            QScrollBar::handle:vertical:hover {
                background: rgba(255, 175, 85, 180);
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
                background: transparent;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

    def run_loader(self, function, result_callback, error_callback, *args):
        worker = DataLoader(function, *args)
        self._workers.append(worker)

        worker.resultReady.connect(result_callback)
        worker.errorOccurred.connect(error_callback)
        worker.finished.connect(
            lambda current=worker: self._workers.remove(current)
            if current in self._workers else None
        )

        worker.start()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_history()

    def load_history(self):
        if self._history_loading:
            return

        self._history_loading = True
        self._history_items = []
        self._has_more_history = False
        self.load_more_button.hide()
        self.refresh_button.setEnabled(False)
        self.status_label.setText(tr("Загружаем историю поисков..."))
        self.show_state("loading")

        self.run_loader(
            self.backend_client.get_history,
            self.on_history_loaded,
            self.on_history_error,
            0,
            self.PAGE_SIZE,
        )

    def load_more_history(self):
        if self._history_loading or not self._has_more_history:
            return

        self._history_loading = True
        self.load_more_button.setEnabled(False)
        self.status_label.setText(tr("Загружаем ещё записи..."))

        self.run_loader(
            self.backend_client.get_history,
            self.on_history_more_loaded,
            self.on_history_more_error,
            len(self._history_items),
            self.PAGE_SIZE,
        )

    def on_history_loaded(self, items):
        self._history_loading = False
        self.refresh_button.setEnabled(True)

        if not isinstance(items, list):
            self.on_history_error(
                tr("Сервер вернул некорректный формат истории.")
            )
            return

        self._history_items = [
            item for item in items if isinstance(item, dict)
        ]
        self._has_more_history = len(items) == self.PAGE_SIZE
        self.count_label.setText(
            tr("Поисков: ") + str(len(self._history_items))
        )
        self.status_label.setText("")

        self.render_history()

    def on_history_more_loaded(self, items):
        self._history_loading = False
        self.load_more_button.setEnabled(True)

        if not isinstance(items, list):
            self.on_history_more_error(
                tr("Сервер вернул некорректный формат истории.")
            )
            return

        self._history_items.extend(
            item for item in items if isinstance(item, dict)
        )
        self._has_more_history = len(items) == self.PAGE_SIZE
        self.count_label.setText(
            tr("Поисков: ") + str(len(self._history_items))
        )
        self.status_label.setText("")
        self.render_history()

    def on_history_more_error(self, error):
        self._history_loading = False
        self.load_more_button.setEnabled(True)
        self.status_label.setText(
            tr("Не удалось загрузить историю.") + "\n" + str(error)
        )

    def on_history_error(self, error):
        self._history_loading = False
        self.refresh_button.setEnabled(True)
        self.count_label.setText(tr("История недоступна"))
        self.status_label.setText(
            tr("Не удалось загрузить историю.") + "\n" + str(error)
        )
        self._history_items = []
        self._has_more_history = False
        self.load_more_button.hide()
        self.show_state("error")

    def render_history(self):
        self.clear_cards()
        self._open_buttons.clear()

        if not self._history_items:
            self.show_state("empty")
            return

        self._state_key = None

        for item in self._history_items:
            card = self.create_history_card(item)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch(1)
        self.load_more_button.setVisible(self._has_more_history)

    def create_history_card(self, item):
        search_id = item.get("id")
        params = item.get("search_params") or {}

        make = str(params.get("make") or "").strip()
        model = str(params.get("model") or "").strip()
        title = " ".join(part for part in (make, model) if part)

        if not title:
            car_type = params.get("car_type")
            if car_type == "electric":
                title = tr("Электромобиль")
            elif car_type == "combustion":
                title = tr("ДВС / Гибрид")
            else:
                title = tr("Поиск") + f" #{search_id}"

        card = QFrame()
        card.setObjectName("historyCard")
        card.setMinimumHeight(112)
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        row_layout = QHBoxLayout(card)
        row_layout.setContentsMargins(20, 15, 16, 15)
        row_layout.setSpacing(18)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setObjectName("historyTitle")
        title_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        details_label = QLabel(self.format_search_params(params))
        details_label.setObjectName("historyDetails")
        details_label.setWordWrap(True)

        meta_text = (
            f"{self.format_date(item.get('created_at'))}"
            f"   •   {self.format_status(item.get('status'))}"
            f"   •   ID #{search_id}"
        )
        meta_label = QLabel(meta_text)
        meta_label.setObjectName("historyMeta")

        text_layout.addWidget(title_label)
        text_layout.addWidget(details_label)
        text_layout.addWidget(meta_label)

        row_layout.addLayout(text_layout, 1)

        open_button = QPushButton(tr("Открыть"))
        open_button.setObjectName("historyOpenButton")
        open_button.setCursor(Qt.CursorShape.PointingHandCursor)
        open_button.setMinimumSize(104, 42)
        open_button.clicked.connect(
            lambda checked=False, sid=search_id: self.open_search(sid)
        )
        row_layout.addWidget(
            open_button,
            0,
            Qt.AlignmentFlag.AlignVCenter
        )

        self._open_buttons[search_id] = open_button
        return card

    @staticmethod
    def format_date(value):
        if not value:
            return tr("Дата не указана")

        try:
            parsed = datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            )
            if parsed.tzinfo is not None:
                parsed = parsed.astimezone()
            return parsed.strftime("%d.%m.%Y  %H:%M")
        except (TypeError, ValueError):
            return str(value)

    @staticmethod
    def format_status(value):
        statuses = {
            "completed": tr("Завершён"),
            "failed": tr("Ошибка"),
            "processing": tr("В процессе"),
        }
        return statuses.get(str(value), str(value or tr("Неизвестно")))

    @staticmethod
    def format_search_params(params):
        parts = []

        year = params.get("year")
        if year:
            parts.append(f"{tr('Год')}: {year}")

        mileage = params.get("mileage", params.get("mileage_km"))
        if mileage is not None:
            try:
                mileage_text = f"{int(mileage):,}".replace(",", " ")
            except (TypeError, ValueError):
                mileage_text = str(mileage)
            parts.append(f"{tr('Пробег')}: {mileage_text} {tr('км')}")

        fuel = params.get("fuel")
        if fuel:
            parts.append(str(fuel))

        engine_volume = params.get("engine_volume", params.get("engine_volume_l"))
        if engine_volume is not None:
            try:
                engine_text = f"{float(engine_volume):g}"
            except (TypeError, ValueError):
                engine_text = str(engine_volume)
            parts.append(f"{tr('Двигатель')}: {engine_text} {tr('л')}")

        gearbox = params.get("gearbox")
        if gearbox:
            parts.append(str(gearbox))

        drive = params.get("drive", params.get("drive_type"))
        if drive:
            parts.append(str(drive))

        return "   •   ".join(parts) if parts else tr("Параметры не указаны")

    def open_search(self, search_id):
        if self._details_loading or search_id is None:
            return

        self._details_loading = True
        self._active_search_id = search_id
        self.status_label.setText(
            tr("Загружаем сохранённый поиск") + f" #{search_id}..."
        )

        button = self._open_buttons.get(search_id)
        if button is not None:
            button.setEnabled(False)
            button.setText(tr("Загрузка..."))

        self.run_loader(
            self.backend_client.get_search_details,
            self.on_search_details_loaded,
            self.on_search_details_error,
            search_id,
        )

    def on_search_details_loaded(self, details):
        self._details_loading = False
        search_id = self._active_search_id
        self._active_search_id = None
        self.restore_open_button(search_id)

        if not isinstance(details, dict):
            self.on_search_details_error(
                tr("Сервер вернул некорректный формат поиска.")
            )
            return

        cars = details.get("cars") or []
        if not isinstance(cars, list):
            cars = []

        result = {
            "search_id": details.get("id", search_id),
            "cars": cars,
            "analysis": details.get("gpt_analysis") or "",
            "analysis_error": None,
            # История хранит сохранённые объявления, но не исходные
            # счётчики найденных и неудачно загруженных объявлений.
            "total_found": None,
            "failed_count": None,
            "status": details.get("status", "completed"),
            "search_params": details.get("search_params") or {},
            "gpt_model": details.get("gpt_model"),
            "is_history": True,
        }

        self.status_label.setText("")
        self.resultRequested.emit(result)

    def on_search_details_error(self, error):
        self._details_loading = False
        search_id = self._active_search_id
        self._active_search_id = None
        self.restore_open_button(search_id)
        self.status_label.setText(
            tr("Не удалось открыть сохранённый поиск.") + "\n" + str(error)
        )

    def restore_open_button(self, search_id):
        button = self._open_buttons.get(search_id)
        if button is not None:
            button.setEnabled(True)
            button.setText(tr("Открыть"))

    def clear_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def show_state(self, state_key):
        self.clear_cards()
        self._open_buttons.clear()
        self.load_more_button.hide()
        self._state_key = state_key

        messages = {
            "loading": tr("Загружаем историю поисков..."),
            "empty": tr("Пока нет сохранённых поисков. Начните поиск — он появится здесь."),
            "error": tr("История временно недоступна. Нажмите «Обновить», чтобы повторить запрос."),
        }

        state_label = QLabel(messages.get(state_key, ""))
        state_label.setObjectName("historyStatus")
        state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        state_label.setWordWrap(True)
        state_label.setMinimumHeight(130)
        self.cards_layout.addWidget(state_label)
        self.cards_layout.addStretch(1)

    def retranslate(self):
        """Обновляет подписи и карточки после смены языка."""
        self.title_label.setText(tr("История поисков"))
        self.subtitle_label.setText(
            tr("Ранее выполненные поиски и сохранённые результаты.")
        )
        self.refresh_button.setText(tr("Обновить"))
        self.load_more_button.setText(tr("Загрузить ещё"))

        if self._history_items:
            self.count_label.setText(
                tr("Поисков: ") + str(len(self._history_items))
            )
            self.render_history()
        elif self._state_key:
            self.show_state(self._state_key)

    def closeEvent(self, event):
        for worker in self._workers:
            worker.requestInterruption()
            worker.wait()
        super().closeEvent(event)
