import unicodedata
from app.localization import tr
from PySide6.QtCore import Qt, QThread, Signal, QEvent
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QComboBox,
    QToolButton,
    QCompleter,
    QSpinBox,
    QPushButton,
    QFrame,
    QMessageBox,
)
from backend_client import BackendClient

# Каталог BEV-моделей для фильтрации общего справочника AUTO.RIA (костыль)
# Модели с разными силовыми установками дополнительно ограничиваются fuel_id.
ELECTRIC_MODELS = {
    "tesla": "Model 3|Model Y|Model S|Model X|Cybertruck",
    "nissan": "Leaf|Ariya|e-NV200|Sakura|Micra EV",
    "volkswagen": "ID.3|ID.4|ID.4 Crozz|ID.5|ID.6|ID.6 Crozz|ID.7|ID. Buzz|ID. Unyx|e-Golf|e-Up",
    "hyundai": "Ioniq|Ioniq Electric|Ioniq 5|Ioniq 6|Ioniq 9|Kona|Kona Electric|Inster",
    "renault": "Zoe|Megane E-Tech|Scenic E-Tech|5 E-Tech|4 E-Tech|Twingo Z.E.|Kangoo Z.E.|Twizy|Fluence Z.E.",
    "audi": "e-tron|Q4 e-tron|Q6 e-tron|Q8 e-tron|A6 e-tron|e-tron GT",
    "kia": "Soul EV|e-Niro|Niro|Niro EV|EV3|EV4|EV5|EV6|EV9|PV5",
    "honda": "e|Honda e|e:Ny1|Prologue|e:NS1|e:NP1",
    "bmw": "i3|i4|i5|i7|iX|iX1|iX2|iX3",
    "mercedesbenz": "EQA|EQB|EQC|EQE|EQS|EQE SUV|EQS SUV|EQV|CLA Electric|G 580",
    "jaguar": "I-Pace",
    "zeekr": "001|001 FR|007|007 GT|009|7X|X|Mix",
    "byd": "Dolphin|Atto 2|Atto 3|Yuan Up|Yuan Plus|Seal|Seal U|Sealion 7|Sea Lion 7|Sea Lion 06|Han|Tang|M6|Seagull|E2|Leopard 3|Song L|Song Plus|e6",
    "chevrolet": "Bolt|Bolt EV|Bolt EUV|Spark EV|Equinox EV|Blazer EV|Silverado EV|Menlo",
    "ford": "Mustang Mach-E|F-150 Lightning|E-Transit|Explorer EV|Capri EV",
    "toyota": "bZ4X|C-HR+|Urban Cruiser EV|RAV4 EV|iQ EV",
    "fiat": "500e|600e|Grande Panda Electric|E-Ducato|e-Doblo|e-Scudo",
    "peugeot": "e-208|e-2008|e-308|e-3008|e-5008|e-Rifter|e-Expert|e-Traveller",
    "porsche": "Taycan|Macan Electric|Macan EV|Cayenne Electric",
    "mitsubishi": "i-MiEV|Minicab MiEV|eK X EV",
    "citroen": "C-Zero|ë-C3|e-C3|ë-C4|e-C4|ë-C4 X|e-C4 X|ë-Berlingo|e-Berlingo|e-Jumpy|e-SpaceTourer",
    "opel": "Ampera-e|Corsa-e|Corsa Electric|Mokka-e|Mokka Electric|Astra Electric|Frontera Electric|Grandland Electric|Combo-e|Zafira-e",
    "volvo": "C40 Recharge|XC40 Recharge|EX30|EX40|EC40|EX90|ES90",
    "mg": "ZS EV|MG4|MG4 EV|MG5 EV|Marvel R|MGS5 EV|Cyberster",
    "polestar": "Polestar 2|Polestar 3|Polestar 4|Polestar 5|2|3|4|5",
    "lucid": "Air|Gravity",
    "mini": "Cooper SE|Cooper Electric|Aceman|Countryman Electric",
    "lexus": "UX 300e|RZ",
    "smart": "EQ fortwo|EQ forfour|fortwo Electric Drive|#1|#3|#5|Smart #1|Smart #3|Smart #5",
    "mazda": "MX-30|Mazda6e|EZ-6",
    "subaru": "Solterra|Trailseeker|Uncharted",
    "genesis": "GV60|Electrified GV70|Electrified G80",
    "avatr": "06|07|11|12",
    "changan": "Eado EV|Eado|E-Star|E-Pro|CS55 E-Rock|T10EV|EM-80|EM-60|Qiyuan Q05|Auchan A600EV|OLV EV",
    "deepal": "S05|S07|SL03|L07",
    "denza": "N7|Z9 GT|D9",
    "geely": "Geometry C|Geometry A|Geometry E|EX5|Galaxy E5|Galaxy E8|Emgrand EV|Emgrand EV Pro|E200|E6|F3E|V6E|H8E",
    "leapmotor": "T03|B10|B01|C10|C11|C16|C01",
    "maxus": "MIFA 9|Euniq 5|Euniq 6|eDeliver 3|eDeliver 5|eDeliver 9|T90 EV",
    "xiaomi": "SU7|SU7 Ultra|YU7",
    "gac": "Aion S|Aion Y|Aion V|Aion LX|Aion UT|S|Y|V|LX|UT|Hyptec HT",
    "skywell": "ET5|BE11",
    "voyah": "Free|Free EV|Dreamer|Dreamer EV|Passion|Passion EV|Courage",
    "hongqi": "E-QM5|E-HS9|EH7|EHS7|Tiangong 08|Tiangong 05",
    "nio": "ET5|ET5 Touring|ET7|EL6|EL7|EL8|ES6|ES7|ES8|EC6|EC7|ET9",
    "xpeng": "G3|G6|G9|P5|P7|P7+|X9|Mona M03",
    "dongfeng": "Nammi Box|Nano Box|EX1|E70",
    "jac": "iEV7S|E-JS4|E10X|Yiwei 3",
    "ora": "03|Ora 03|Good Cat|07|Ora 07|Lightning Cat|Ballet Cat",
    "gwm": "03|Ora 03|Good Cat|07|Ora 07|Lightning Cat|Ballet Cat",
    "chery": "eQ1|eQ5|eQ7|iCar 03|iCar V23",
    "lynkco": "Z10|Z20",
    "omoda": "E5|OMODA E5",
    "dsautomobiles": "DS 3 E-Tense|DS 3 E-TENSE|N°8|No 8",
    "alfaromeo": "Junior Elettrica|Junior",
    "abarth": "500e|600e",
    "jeep": "Avenger Electric|Wagoneer S",
    "cadillac": "Optiq|Lyriq|Vistiq|Escalade IQ|Celestiq",
    "gmc": "Hummer EV|HUMMER EV Pickup|HUMMER EV SUV|Sierra EV",
    "rivian": "R1T|R1S|R2",
    "lotus": "Eletre|Emeya",
    "maserati": "GranTurismo Folgore|Grecale Folgore",
    "rollsroyce": "Spectre",
    "dacia": "Spring",
    "lancia": "Ypsilon Electric|Ypsilon",
    "kgm": "Torres EVX|Musso EV",
    "vinfast": "VF 3|VF 5|VF 6|VF 7|VF 8|VF 9",
    "leopard": "3|Leopard 3",
    "skoda": "Enyaq|Enyaq Coupe|Elroq|Peaq",
    "suzuki": "e VITARA",
    "huawei": "Aito M5 EV|Aito M9 EV|Aito M5|Aito M9|M5 EV|M9 EV|Luxeed S7|Luxeed R7",
    "aito": "Aito M5 EV|Aito M9 EV|Aito M5|Aito M9|M5 EV|M9 EV",
}

# Разные варианты написания марок в справочнике AUTO.RIA.
BRAND_ALIASES = {
    "mercedes": "mercedesbenz",
    "vw": "volkswagen",
    "ds": "dsautomobiles",
    "gacaion": "gac",
    "aion": "gac",
    "greatwall": "gwm",
}


def normalize_name(value):
    """Нормализует регистр, диакритику и знаки препинания в названии."""
    normalized = unicodedata.normalize("NFKD", str(value).casefold())
    normalized = "".join(
        character for character in normalized
        if not unicodedata.combining(character))
    return "".join(character for character in normalized if character.isalnum())


def get_brand_key(brand_name):
    """Возвращает ключ марки из каталога электромобилей."""
    normalized = normalize_name(brand_name)
    return BRAND_ALIASES.get(normalized, normalized)


def is_electric_model(model_name, allowed_models):
    """Проверяет, входит ли модель из AUTO.RIA в каталог BEV-моделей."""
    normalized_model = normalize_name(model_name)
    if not normalized_model:
        return False
    for allowed_name in allowed_models:
        normalized_allowed = normalize_name(allowed_name)
        if not normalized_allowed:
            continue
        if normalized_model == normalized_allowed:
            return True
        # Учитываем уточнения в названии модели; короткие коды сравниваем точно.
        if len(normalized_allowed) >= 4 and normalized_model.startswith(normalized_allowed):
            return True
    return False


class DataLoader(QThread):
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


class ElectricPage(QWidget):
    searchRequested = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setObjectName("electricPage")
        self._workers = []
        self.backend_client = BackendClient()
        self.electric_fuel_id = None
        self.init_ui()
        self.apply_styles()
        self.load_references()

    @staticmethod
    def make_searchable(combo, placeholder):
        """Разрешает искать марку или модель вводом текста."""
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.setMaxVisibleItems(15)

        line_edit = combo.lineEdit()
        line_edit.setPlaceholderText(tr(placeholder))
        line_edit.setClearButtonEnabled(True)

        completer = QCompleter(combo.model(), combo)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        combo.setCompleter(completer)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        title = QLabel("Поиск электромобилей")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Выберите параметры электромобиля для анализа рынка")
        subtitle.setObjectName("pageSubtitle")
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("formCard")

        form_layout = QFormLayout(card)
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setHorizontalSpacing(25)
        form_layout.setVerticalSpacing(18)

        self.brand_combo = QComboBox()
        self.brand_combo.addItem("Загрузка марок...", None)
        self.brand_combo.setEnabled(False)
        self.make_searchable(
            self.brand_combo,
            "Начните вводить марку..."
        )

        self.model_combo = QComboBox()
        self.model_combo.addItem("Сначала выберите марку", None)
        self.model_combo.setEnabled(False)
        self.make_searchable(
            self.model_combo,
            "Начните вводить модель..."
        )

        self.year_input = QSpinBox()
        self.year_input.setRange(1900, 2027)
        self.year_input.setValue(2020)
        self.year_input.setSuffix(tr(" год"))

        self.mileage_input = QSpinBox()
        self.mileage_input.setRange(0, 1_000_000)
        self.mileage_input.setValue(60_000)
        self.mileage_input.setSingleStep(5_000)
        self.mileage_input.setSuffix(tr(" км"))

        form_layout.addRow("Марка автомобиля:", self.brand_combo)
        form_layout.addRow("Модель:", self.model_combo)
        form_layout.addRow("Год выпуска:", self.year_input)
        form_layout.addRow("Пробег:", self.mileage_input)

        main_layout.addWidget(card)

        self.status_label = QLabel(
            "Загружаем справочники AUTO.RIA..."
        )
        self.status_label.setObjectName("statusLabel")

        main_layout.addWidget(self.status_label)
        main_layout.addStretch()

        self.search_button = QPushButton("Начать поиск")
        self.search_button.setObjectName("primaryButton")
        self.search_button.setMinimumHeight(48)
        self.search_button.setEnabled(False)

        main_layout.addWidget(self.search_button)

        self.brand_combo.currentIndexChanged.connect(
            self.on_brand_changed)
        self.model_combo.currentIndexChanged.connect(
            self.update_search_button)
        self.search_button.clicked.connect(
            self.start_search)

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget#electricPage {
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

            QComboBox, QSpinBox {
                background-color: #353535;
                color: white;
                border: 1px solid #505050;
                border-radius: 7px;
                padding: 9px;
                min-height: 25px;
            }

            QComboBox:hover, QSpinBox:hover {
                border: 1px solid #0078d4;
            }

            /* Более широкая и удобная зона раскрытия списка. */
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 36px;
                border-left: 1px solid #505050;
                border-top-right-radius: 7px;
                border-bottom-right-radius: 7px;
            }


            QComboBox QLineEdit {
                padding-right: 36px;
            }

            QToolButton#comboArrowButton {
                color: #E8E8E8;
                background-color: #353535;
                border: none;
                border-left: 1px solid #505050;
                border-top-right-radius: 7px;
                border-bottom-right-radius: 7px;
                font-size: 11px;
                padding: 0px;
            }

            QToolButton#comboArrowButton:hover {
                background-color: #454545;
            }

            QToolButton#comboArrowButton:disabled {
                color: #777777;
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

        # Отдельная кнопка со стрелкой поверх правой части каждого списка.
        for combo in self.findChildren(QComboBox):
            arrow_button = QToolButton(combo)
            arrow_button.setObjectName("comboArrowButton")
            arrow_button.setText("▼")
            arrow_button.setCursor(Qt.CursorShape.PointingHandCursor)
            arrow_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            arrow_button.clicked.connect(
                lambda checked=False, current_combo=combo: current_combo.showPopup()
            )
            combo.installEventFilter(self)
            self._position_combo_arrow(combo)

    @staticmethod
    def _position_combo_arrow(combo):
        arrow_button = combo.findChild(QToolButton, "comboArrowButton")
        if arrow_button is not None:
            button_width = min(36, combo.width())
            arrow_button.setGeometry(
                combo.width() - button_width - 1,
                1,
                button_width,
                max(0, combo.height() - 2),
            )
            arrow_button.raise_()

    def eventFilter(self, watched, event):
        if isinstance(watched, QComboBox) and event.type() == QEvent.Type.Resize:
            self._position_combo_arrow(watched)
        return super().eventFilter(watched, event)

    def run_loader(self, function, callback, *args):
        worker = DataLoader(function, *args)
        self._workers.append(worker)
        worker.resultReady.connect(callback)
        worker.errorOccurred.connect(self.on_loading_error)
        worker.finished.connect(
            lambda w=worker: self._workers.remove(w)
            if w in self._workers else None)
        worker.start()

    def load_references(self):
        self.status_label.setText(
            tr("Загружаем марки AUTO.RIA..."))
        self.run_loader(
            self.backend_client.get_marks,
            self.on_marks_loaded)
        self.run_loader(
            self.backend_client.get_fuel_types,
            self.on_fuel_types_loaded)

    def on_marks_loaded(self, marks):
        electric_marks = [
            item for item in marks
            if isinstance(item, dict)
               and get_brand_key(item.get("name", "")) in ELECTRIC_MODELS]

        self.fill_combo(self.brand_combo, electric_marks)
        self.brand_combo.setEnabled(bool(electric_marks))
        if electric_marks:
            self.status_label.setText(
                tr("Выберите марку электромобиля."))
        else:
            self.status_label.setText(
                tr("В справочнике AUTO.RIA не найдены марки из каталога электромобилей."))

    def on_fuel_types_loaded(self, fuel_types):
        self.electric_fuel_id = None
        for item in fuel_types:
            if not isinstance(item, dict):
                continue
            fuel_name = normalize_name(item.get("name", ""))
            if fuel_name in {"електро", "электро", "electric", "electricity"}:
                fuel_id = item.get("value")
                if fuel_id is not None:
                    try:
                        self.electric_fuel_id = int(fuel_id)
                    except (TypeError, ValueError):
                        self.electric_fuel_id = None
                break

        if self.electric_fuel_id is None:
            self.status_label.setText(
                tr("Не удалось определить тип топлива «Електро». Поиск временно недоступен."))
        self.update_search_button()

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
            self.model_combo.blockSignals(True)
            self.model_combo.clear()
            self.model_combo.addItem(
                tr("Сначала выберите марку"),
                None
            )
            self.model_combo.blockSignals(False)
            self.model_combo.setEnabled(False)
            self.search_button.setEnabled(False)
            return
        self.model_combo.clear()
        self.model_combo.addItem(tr("Загрузка моделей..."), None)
        self.model_combo.setEnabled(False)
        self.search_button.setEnabled(False)
        self.status_label.setText(
            tr("Загружаем модели выбранной марки..."))
        self.run_loader(
            self.backend_client.get_models,
            self.on_models_loaded,
            brand_id)

    def on_models_loaded(self, models):
        brand_key = get_brand_key(self.brand_combo.currentText())
        allowed_models = ELECTRIC_MODELS.get(brand_key, "").split("|")
        electric_models = [
            item for item in models
            if isinstance(item, dict)
               and is_electric_model(item.get("name", ""), allowed_models)]
        self.fill_combo(self.model_combo, electric_models)
        self.model_combo.setEnabled(bool(electric_models))
        if electric_models:
            self.status_label.setText(
                tr("Выберите модель и укажите год и пробег."))
        else:
            self.status_label.setText(
                tr("Для этой марки пока нет моделей, совпадающих с каталогом электромобилей."))
        self.update_search_button()

    def update_search_button(self):
        ready = (
                self.brand_combo.currentData() is not None
                and self.model_combo.currentData() is not None
                and self.electric_fuel_id is not None)
        self.search_button.setEnabled(ready)

    def on_loading_error(self, error):
        self.status_label.setText(
            tr("Ошибка загрузки справочников."))

        QMessageBox.critical(
            self,
            tr("Ошибка AUTO.RIA"),
            tr("Не удалось загрузить данные:\n\n") + str(error))

    def start_search(self):
        brand_id = self.brand_combo.currentData()
        model_id = self.model_combo.currentData()
        if brand_id is None or model_id is None:
            QMessageBox.warning(
                self,
                tr("Не выбрана модель"),
                tr("Выберите марку и модель автомобиля."))
            return
        if self.electric_fuel_id is None:
            QMessageBox.warning(
                self,
                tr("Не определён тип топлива"),
                tr("Не удалось определить ID топлива «Електро» в справочнике AUTO.RIA."))
            return
        search_data = {
            "car_type": "electric",
            "make": self.brand_combo.currentText(),
            "brand_id": brand_id,
            "model": self.model_combo.currentText(),
            "model_id": model_id,
            "year": self.year_input.value(),
            "mileage": self.mileage_input.value(),
            "fuel": "Електро",
            "fuel_id": self.electric_fuel_id,
        }
        self.searchRequested.emit(search_data)

    def closeEvent(self, event):
        for worker in self._workers:
            worker.requestInterruption()
            worker.wait()

        super().closeEvent(event)