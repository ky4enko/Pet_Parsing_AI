from app.localization import tr
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QFrame,
    QMessageBox,
)

from backend_client import BackendClient

class DataLoader(QThread):
    """Загружает справочники AUTO.RIA в фоновом потоке."""

    resultReady = Signal(object)
    errorOccurred = Signal(str)

    def __init__(self, function, *args):
        super().__init__()
        self.function = function
        self.args = args

    def run(self):
        try:
            result = self.function(*self.args)
            self.resultReady.emit(result)
        except Exception as error:
            self.errorOccurred.emit(str(error))


class CombustionPage(QWidget):

    searchRequested = Signal(dict)

    def __init__(self):
        super().__init__()

        self.setObjectName("combustionPage")

        self._workers = []
        self.backend_client = BackendClient()

        self.init_ui()
        self.apply_styles()
        self.load_references()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        title = QLabel("Поиск автомобилей с ДВС")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Настройте параметры автомобиля для анализа рынка"
        )
        subtitle.setObjectName("pageSubtitle")

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # Карточка с параметрами
        card = QFrame()
        card.setObjectName("formCard")

        form_layout = QFormLayout(card)
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setHorizontalSpacing(25)
        form_layout.setVerticalSpacing(18)

        # Марка
        self.brand_combo = QComboBox()
        self.brand_combo.addItem("Загрузка марок...", None)
        self.brand_combo.setEnabled(False)

        # Модель
        self.model_combo = QComboBox()
        self.model_combo.addItem("Сначала выберите марку", None)
        self.model_combo.setEnabled(False)

        # Год
        self.year_input = QSpinBox()
        self.year_input.setRange(1900, 2027)
        self.year_input.setValue(2018)
        self.year_input.setSuffix(tr(" год"))

        # Пробег
        self.mileage_input = QSpinBox()
        self.mileage_input.setRange(0, 1_000_000)
        self.mileage_input.setValue(100_000)
        self.mileage_input.setSingleStep(5_000)
        self.mileage_input.setSuffix(tr(" км"))

        # Топливо
        self.fuel_combo = QComboBox()
        self.fuel_combo.addItem("Загрузка...", None)
        self.fuel_combo.setEnabled(False)

        # Объём двигателя
        self.engine_input = QDoubleSpinBox()
        self.engine_input.setRange(0.1, 10.0)
        self.engine_input.setValue(2.0)
        self.engine_input.setSingleStep(0.1)
        self.engine_input.setSuffix(tr(" л"))

        # Коробка передач
        self.gearbox_combo = QComboBox()
        self.gearbox_combo.addItem("Загрузка...", None)
        self.gearbox_combo.setEnabled(False)

        # Привод
        self.drive_combo = QComboBox()
        self.drive_combo.addItem("Загрузка...", None)
        self.drive_combo.setEnabled(False)

        form_layout.addRow("Марка автомобиля:", self.brand_combo)
        form_layout.addRow("Модель:", self.model_combo)
        form_layout.addRow("Год выпуска:", self.year_input)
        form_layout.addRow("Пробег:", self.mileage_input)
        form_layout.addRow("Тип топлива:", self.fuel_combo)
        form_layout.addRow("Объём двигателя:", self.engine_input)
        form_layout.addRow("Коробка передач:", self.gearbox_combo)
        form_layout.addRow("Привод:", self.drive_combo)

        main_layout.addWidget(card)

        # Статус загрузки
        self.status_label = QLabel(tr("Загружаем справочники AUTO.RIA..."))
        self.status_label.setObjectName("statusLabel")

        main_layout.addWidget(self.status_label)

        main_layout.addStretch()

        # Кнопка поиска
        self.search_button = QPushButton("Начать поиск")
        self.search_button.setObjectName("primaryButton")
        self.search_button.setMinimumHeight(48)
        self.search_button.setEnabled(False)

        main_layout.addWidget(self.search_button)

        # Сигналы
        self.brand_combo.currentIndexChanged.connect(
            self.on_brand_changed
        )

        self.search_button.clicked.connect(
            self.start_search
        )

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget#combustionPage {
                background-color: #202020;
            }

            QLabel#pageTitle {
                color: white;
                font-size: 30px;
                font-weight: 700;
            }

            QLabel#pageSubtitle {
                color: #aaaaaa;
                font-size: 14px;
            }

            QFrame#formCard {
                background-color: #292929;
                border: 1px solid #3b3b3b;
                border-radius: 14px;
            }

            QLabel {
                color: #dddddd;
                font-size: 14px;
            }

            QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #353535;
                color: white;
                border: 1px solid #505050;
                border-radius: 7px;
                padding: 9px;
                min-height: 25px;
            }

            QComboBox:hover, QSpinBox:hover,
            QDoubleSpinBox:hover {
                border: 1px solid #0078d4;
            }

            QComboBox QAbstractItemView {
                background-color: #353535;
                color: white;
                selection-background-color: #0078d4;
            }

            QLabel#statusLabel {
                color: #999999;
                font-size: 12px;
            }

            QPushButton#primaryButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
            }

            QPushButton#primaryButton:hover {
                background-color: #1689e8;
            }

            QPushButton#primaryButton:disabled {
                background-color: #454545;
                color: #888888;
            }
        """)

    def run_loader(self, function, callback, *args):
        """Запускает загрузку данных в отдельном потоке."""

        worker = DataLoader(function, *args)
        self._workers.append(worker)

        worker.resultReady.connect(callback)
        worker.errorOccurred.connect(self.on_loading_error)

        worker.finished.connect(
            lambda w=worker: self._workers.remove(w)
            if w in self._workers else None
        )

        worker.start()

    def load_references(self):
        """Загружает основные справочники."""

        self.status_label.setText(
            tr("Загружаем справочники AUTO.RIA...")
        )

        self.run_loader(
            self.load_all_references,
            self.on_references_loaded
        )

    def load_all_references(self):
        return {
            "marks": self.backend_client.get_marks(),
            "fuel": self.backend_client.get_fuel_types(),
            "gearboxes": self.backend_client.get_gearboxes(),
            "drives": self.backend_client.get_drive_types(),
        }

    def on_references_loaded(self, data):
        self.fill_combo(self.brand_combo, data["marks"])
        self.fill_combo(self.fuel_combo, data["fuel"])
        self.fill_combo(self.gearbox_combo, data["gearboxes"])
        self.fill_combo(self.drive_combo, data["drives"])

        self.brand_combo.setEnabled(True)
        self.fuel_combo.setEnabled(True)
        self.gearbox_combo.setEnabled(True)
        self.drive_combo.setEnabled(True)

        self.status_label.setText(
            tr("Справочники загружены. Выберите марку автомобиля.")
        )

    @staticmethod
    def fill_combo(combo, items):
        combo.blockSignals(True)
        combo.clear()

        for item in items:
            name = item.get("name")
            value = item.get("value")

            if name is not None and value is not None:
                combo.addItem(str(name), value)

        combo.blockSignals(False)

    def on_brand_changed(self, index):
        brand_id = self.brand_combo.currentData()

        if brand_id is None:
            return

        self.model_combo.clear()
        self.model_combo.addItem(tr("Загрузка моделей..."), None)
        self.model_combo.setEnabled(False)
        self.search_button.setEnabled(False)

        self.status_label.setText(
            tr("Загружаем модели выбранной марки...")
        )

        self.run_loader(
            self.backend_client.get_models,
            self.on_models_loaded,
            brand_id
        )

    def on_models_loaded(self, models):
        self.fill_combo(self.model_combo, models)

        self.model_combo.setEnabled(True)

        self.status_label.setText(
            tr("Выберите модель и заполните параметры автомобиля.")
        )

        self.update_search_button()

    def update_search_button(self):
        ready = (
            self.brand_combo.currentData() is not None
            and self.model_combo.currentData() is not None
            and self.fuel_combo.currentData() is not None
            and self.gearbox_combo.currentData() is not None
            and self.drive_combo.currentData() is not None
        )

        self.search_button.setEnabled(ready)

    def on_loading_error(self, error):
        self.status_label.setText(tr("Ошибка загрузки справочников."))

        QMessageBox.critical(
            self,
            tr("Ошибка AUTO.RIA"),
            tr("Не удалось загрузить данные:\n\n") + str(error)
        )

    def start_search(self):
        brand_id = self.brand_combo.currentData()
        model_id = self.model_combo.currentData()

        if brand_id is None or model_id is None:
            QMessageBox.warning(
                self,
                tr("Не выбрана модель"),
                tr("Выберите марку и модель автомобиля.")
            )
            return

        year = self.year_input.value()
        mileage = self.mileage_input.value()
        engine_volume = self.engine_input.value()

        search_data = {
            "car_type": "combustion",

            "make": self.brand_combo.currentText(),
            "brand_id": brand_id,

            "model": self.model_combo.currentText(),
            "model_id": model_id,

            "year": year,
            "mileage": mileage,

            "fuel": self.fuel_combo.currentText(),
            "fuel_id": self.fuel_combo.currentData(),

            "engine_volume": engine_volume,

            "gearbox": self.gearbox_combo.currentText(),
            "gearbox_id": self.gearbox_combo.currentData(),

            "drive": self.drive_combo.currentText(),
            "drive_id": self.drive_combo.currentData(),
        }

        self.searchRequested.emit(search_data)

    def closeEvent(self, event):
        for worker in self._workers:
            worker.requestInterruption()
            worker.wait()

        super().closeEvent(event)