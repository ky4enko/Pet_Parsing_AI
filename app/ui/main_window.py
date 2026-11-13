import sys
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QAbstractButton,
    QLabel,
    QGraphicsDropShadowEffect,
    QPushButton,
    QFrame,
    QVBoxLayout,
)

from qfluentwidgets import (
    FluentWindow,
    FluentIcon,
    NavigationItemPosition,
    setTheme,
    Theme,
)

from app.ui.home_page import HomePage
from app.ui.combustion_page import CombustionPage
from app.ui.electric_page import ElectricPage
from app.ui.results_page import ResultsPage
from app.ui.history_page import HistoryPage
from app.ui.search_worker import SearchWorker
from app.ui.theme_manager import ThemeManager
from app.ui.theme_dialog import ThemeDialog
from app.localization import Localization, translate_widget_tree


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()

        setTheme(Theme.DARK)

        self.setWindowTitle("AUTO.RIA Analyzer")
        self.resize(1250, 800)
        self.setMinimumSize(950, 650)

        self.background_labels = {}
        self.search_worker = None
        self._results_source = None
        self.localization = Localization()
        self.language_buttons = {}
        self.language_menu_open = False

        # Менеджер оформления
        self.theme_manager = ThemeManager()
        self.theme_dialog = None

        self.init_navigation()
        self.apply_navigation_style()
        self.connect_signals()
        self.create_language_switcher()
        self.localization.languageChanged.connect(self.apply_language)
        self.apply_language(self.localization.language)

        # Применяем сохранённую тему при запуске
        self.apply_theme()

    # язык
    def create_language_switcher(self):
        """Единый компактный переключатель языка в правом нижнем углу."""
        self.language_container = QFrame(self)
        self.language_container.setObjectName("languageContainer")
        self.language_container.setFixedWidth(54)
        self.language_container.setFixedHeight(48)
        self.language_container.setStyleSheet("""
            QFrame#languageContainer {
                background: transparent;
                border: none;
            }
            QPushButton {
                color: rgba(255, 255, 255, 220);
                background-color: rgba(22, 24, 32, 225);
                border: 1px solid rgba(255, 255, 255, 45);
                border-radius: 9px;
                min-width: 44px;
                max-width: 44px;
                min-height: 38px;
                max-height: 38px;
                font-size: 12px;
                font-weight: 600;
                padding: 0;
            }
            QPushButton:hover {
                color: white;
                border: 1px solid rgba(255, 145, 65, 190);
                background-color: rgba(255, 120, 45, 35);
            }
            QPushButton#currentLanguage {
                color: white;
                background-color: rgba(22, 24, 32, 235);
                border: 1px solid rgba(255, 145, 65, 105);
            }
        """)

        # Все три кнопки находятся в одном layout-контейнере.
        # Поэтому они не могут наложиться друг на друга.
        self.language_layout = QVBoxLayout(self.language_container)
        self.language_layout.setContentsMargins(5, 5, 5, 5)
        self.language_layout.setSpacing(6)

        self.language_buttons = {}
        for code in ("uk", "en", "ru"):
            button = QPushButton(Localization.LANGUAGES[code], self.language_container)
            button.setCursor(Qt.PointingHandCursor)
            button.setFixedSize(44, 38)
            button.hide()
            button.clicked.connect(
                lambda checked=False, lang=code: self.localization.set_language(lang)
            )
            self.language_buttons[code] = button
            self.language_layout.addWidget(button)

        self.current_language_button = QPushButton(
            Localization.LANGUAGES[self.localization.language],
            self.language_container
        )
        self.current_language_button.setObjectName("currentLanguage")
        self.current_language_button.setCursor(Qt.PointingHandCursor)
        self.current_language_button.setFixedSize(44, 38)
        self.current_language_button.clicked.connect(self.toggle_language_menu)
        self.language_layout.addWidget(self.current_language_button)

        self.language_container.raise_()
        self.position_language_switcher()
        self.language_container.setVisible(True)

    def toggle_language_menu(self):
        self.language_menu_open = not self.language_menu_open
        self.position_language_switcher()

    def position_language_switcher(self):
        if not hasattr(self, "language_container"):
            return

        available = [
            code for code in ("uk", "en", "ru")
            if code != self.localization.language
        ]

        for code, button in self.language_buttons.items():
            button.setText(Localization.LANGUAGES[code])
            button.setVisible(self.language_menu_open and code in available)

        # 48 px у закритому стані; 136 px — три кнопки зі сталими проміжками.
        self.language_container.setFixedHeight(136 if self.language_menu_open else 48)
        margin = 22
        self.language_container.move(
            self.width() - self.language_container.width() - margin,
            self.height() - self.language_container.height() - margin
        )
        self.language_container.raise_()

    def apply_language(self, language):
        """Обновляет подписи всех страниц и открытых окон."""
        for widget in (self, self.home_page, self.combustion_page,
                       self.electric_page, self.results_page,
                       self.history_page):
            translate_widget_tree(widget, language)

        self.history_page.retranslate()

        if self.theme_dialog is not None and self.theme_dialog.isVisible():
            translate_widget_tree(self.theme_dialog, language)

        self.current_language_button.setText(Localization.LANGUAGES[language])
        self.language_menu_open = False
        self.position_language_switcher()

    # НАВИГАЦИЯ
    def init_navigation(self):

        self.home_page = HomePage()
        self.combustion_page = CombustionPage()
        self.electric_page = ElectricPage()
        self.results_page = ResultsPage()
        self.history_page = HistoryPage()

        self.addSubInterface(
            self.home_page,
            FluentIcon.HOME,
            "Главная",
        )

        self.addSubInterface(
            self.combustion_page,
            FluentIcon.SEARCH,
            "ДВС / Гибрид",
        )

        self.addSubInterface(
            self.electric_page,
            FluentIcon.SEARCH,
            "Электромобили",
        )

        self.addSubInterface(
            self.results_page,
            FluentIcon.DOCUMENT,
            "Результаты",
        )

        self.addSubInterface(
            self.history_page,
            FluentIcon.HISTORY,
            "История",
        )


        # Кнопка оформления внизу панели
        self.navigationInterface.addItem(
            routeKey="theme_settings",
            icon=FluentIcon.PALETTE,
            text="Оформление",
            onClick=self.open_theme_dialog,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        return_button = self.navigationInterface.panel.returnButton
        try:
            return_button.clicked.disconnect()
        except (RuntimeError, TypeError):
            pass
        return_button.clicked.connect(self.return_to_home)
        return_button.setToolTip("На главную")

        # Собственный обработчик кнопки «Назад»
        return_button = self.navigationInterface.panel.returnButton

        try:
            return_button.clicked.disconnect()
        except (RuntimeError, TypeError):
            pass

        return_button.clicked.connect(self.return_to_home)
        return_button.setToolTip("Назад")

        self.switchTo(self.home_page)

    # ОФОРМЛЕНИЕ БОКОВОЙ ПАНЕЛИ
    def apply_navigation_style(self):

        nav = self.navigationInterface

        # Фон и рамка панели
        nav.setStyleSheet("""
            NavigationInterface {
                background-color: rgba(15, 16, 24, 245);
                border-right: 1px solid rgba(255, 135, 55, 95);
            }
        """)

        self.navigation_glow = QGraphicsDropShadowEffect(nav)
        self.navigation_glow.setBlurRadius(35)
        self.navigation_glow.setOffset(3, 0)
        self.navigation_glow.setColor(
            QColor(255, 112, 42, 95)
        )

        nav.setGraphicsEffect(self.navigation_glow)

        # Оформление кнопок навигации
        button_style = """
            QAbstractButton {
                color: rgba(255, 255, 255, 220);
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 11px;
                margin: 4px 7px;
                padding: 8px;
                text-align: left;
            }

            QAbstractButton:hover {
                color: white;
                background-color: rgba(255, 120, 45, 35);
                border: 1px solid rgba(255, 145, 65, 100);
            }

            QAbstractButton:checked {
                color: white;
                background-color: rgba(255, 110, 35, 55);
                border: 1px solid rgba(255, 145, 65, 175);
            }

            QAbstractButton:pressed {
                background-color: rgba(255, 100, 30, 85);
                border: 1px solid #FF9B35;
            }
        """


        buttons = nav.findChildren(QAbstractButton)

        for button in buttons:
            button.setStyleSheet(button_style)
            button.setAttribute(Qt.WA_Hover, True)

    # ОКНО ПЕРСОНАЛИЗАЦИИ
    def open_theme_dialog(self):

        self.theme_dialog = ThemeDialog(
            self.theme_manager,
            self
        )

        self.theme_dialog.themeChanged.connect(
            self.apply_theme
        )

        translate_widget_tree(self.theme_dialog, self.localization.language)
        self.theme_dialog.exec()

    # ФОНОВОЕ ИЗОБРАЖЕНИЕ
    def apply_theme(self):
        """Устанавливает выбранный фон на всех страницах."""

        pages = [
            self.home_page,
            self.combustion_page,
            self.electric_page,
            self.results_page,
            self.history_page,
        ]

        for page in pages:

            if page not in self.background_labels:

                # Фоновая картинка
                background = QLabel(page)

                background.setAttribute(
                    Qt.WA_TransparentForMouseEvents
                )

                background.setScaledContents(False)

                # Слой затемнения
                overlay = QLabel(background)

                overlay.setStyleSheet(
                    "background-color: transparent;"
                )

                overlay.setAttribute(
                    Qt.WA_TransparentForMouseEvents
                )

                self.background_labels[page] = (
                    background,
                    overlay
                )

                page.installEventFilter(self)

            self.update_page_background(page)

    def update_page_background(self, page):
        """Обновляет фон с учётом размера страницы."""

        background, overlay = self.background_labels[page]

        size = page.size()

        background.setGeometry(
            0,
            0,
            size.width(),
            size.height()
        )

        overlay.setGeometry(
            0,
            0,
            size.width(),
            size.height()
        )

        pixmap = self.theme_manager.get_background_pixmap(size)

        background.setPixmap(pixmap)

        # Фон отправляется за остальные элементы
        background.lower()

        background.show()
        overlay.show()

    def return_to_home(self):
        """
        Поведение стрелки:
        - обычный поиск -> Главная;
        - отчёт из истории -> История;
        - список истории -> Главная.
        """

        current_page = self.stackedWidget.currentWidget()

        # Если открыт отчёт из истории,
        # сначала возвращаемся к списку отчётов.
        if (
                current_page is self.results_page
                and self._results_source == "history"
        ):
            self._results_source = None
            self.switchTo(self.history_page)
            return

        # Во всех остальных случаях возвращаемся на Главную.
        self._results_source = None
        self.switchTo(self.home_page)

        # Очищаем старую историю переходов.
        router = self.navigationInterface.panel.history

        stacked_history = router.stackHistories.get(self.stackedWidget)

        if stacked_history is not None:
            stacked_history.history = [self.home_page.objectName()]

        router.history = [
            item for item in router.history
            if item.stacked is not self.stackedWidget
        ]

        router.emptyChanged.emit(not bool(router.history))

    def switchTo(self, interface):
        """Показывает переключатель языка только на главной странице."""
        super().switchTo(interface)

        if hasattr(self, "language_container"):
            is_home = interface is getattr(self, "home_page", None)
            self.language_container.setVisible(is_home)
            if not is_home:
                self.language_menu_open = False
            if is_home:
                self.position_language_switcher()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_language_switcher()

    def eventFilter(self, watched, event):

        if event.type() == QEvent.Resize:

            if watched in self.background_labels:
                self.update_page_background(watched)

        return super().eventFilter(watched, event)

    # --------------------------------------------------
    # СИГНАЛЫ
    # --------------------------------------------------

    def connect_signals(self):

        self.home_page.combustionRequested.connect(
            lambda: self.switchTo(self.combustion_page)
        )

        self.home_page.electricRequested.connect(
            lambda: self.switchTo(self.electric_page)
        )

        self.combustion_page.searchRequested.connect(
            self.start_search
        )

        self.electric_page.searchRequested.connect(
            self.start_search
        )

        self.history_page.resultRequested.connect(
            self.show_history_result
        )

    # РЕЗУЛЬТАТ ИЗ ИСТОРИИ
    def show_history_result(self, result):
        """Открывает сохранённый отчёт из истории."""
        self._results_source = "history"

        self.results_page.show_results(result)
        self.switchTo(self.results_page)

    # ПОИСК АВТОМОБИЛЕЙ
    def start_search(self, search_data):
        if self.search_worker is not None:
            if self.search_worker.isRunning():
                QMessageBox.warning(
                    self,
                    self.localization.tr("Поиск уже выполняется"),
                    self.localization.tr("Дождитесь завершения текущего поиска."))
                return

        # Открываем страницу результатов
        self._results_source = "search"
        self.switchTo(self.results_page)
        self.results_page.show_loading()

        # Создаём фоновый поток
        self.search_worker = SearchWorker(search_data, self.localization.language)
        self.search_worker.progressChanged.connect(
            self.results_page.update_status)
        self.search_worker.resultReady.connect(
            self.on_search_finished)
        self.search_worker.errorOccurred.connect(
            self.on_search_error)
        self.search_worker.start()

    def on_search_finished(self, result):
        self.results_page.show_results(result)
        if self.search_worker is not None:
            self.search_worker.deleteLater()
            self.search_worker = None

    def on_search_error(self, error):
        self.results_page.show_error(error)
        QMessageBox.critical(
            self,
            self.localization.tr("Ошибка поиска"),
            str(error))
        if self.search_worker is not None:
            self.search_worker.deleteLater()
            self.search_worker = None



# ЗАПУСК ПРИЛОЖЕНИЯ
if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
