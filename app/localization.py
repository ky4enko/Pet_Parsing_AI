"""Централизованная локализация интерфейса AUTO.RIA Analyzer."""
from PySide6.QtCore import QObject, QSettings, Signal

TRANSLATIONS = {
    "Главная": {"uk": "Головна", "en": "Home"},
    "ДВС / Гибрид": {"uk": "ДВЗ / Гібрид", "en": "ICE / Hybrid"},
    "Электромобили": {"uk": "Електромобілі", "en": "Electric vehicles"},
    "Результаты": {"uk": "Результати", "en": "Results"},
    "Оформление": {"uk": "Оформлення", "en": "Appearance"},
    "AUTO.RIA Analyzer": {"uk": "AUTO.RIA Analyzer", "en": "AUTO.RIA Analyzer"},
    "AUTO.RIA ANALYZER": {"uk": "AUTO.RIA ANALYZER", "en": "AUTO.RIA ANALYZER"},
    "ДВС / Гибрид": {"uk": "ДВЗ / Гібрид", "en": "ICE / Hybrid"},
    "Начать поиск": {"uk": "Почати пошук", "en": "Start search"},
    "Поиск автомобилей с ДВС": {"uk": "Пошук автомобілів із ДВЗ", "en": "Search combustion cars"},
    "Настройте параметры автомобиля для анализа рынка": {"uk": "Налаштуйте параметри автомобіля для аналізу ринку", "en": "Set vehicle parameters for market analysis"},
    "Загрузка марок...": {"uk": "Завантаження марок...", "en": "Loading brands..."},
    "Сначала выберите марку": {"uk": "Спочатку виберіть марку", "en": "Select a brand first"},
    " год": {"uk": " рік", "en": " year"},
    " км": {"uk": " км", "en": " km"},
    " л": {"uk": " л", "en": " L"},
    "Загрузка...": {"uk": "Завантаження...", "en": "Loading..."},
    "Марка автомобиля:": {"uk": "Марка автомобіля:", "en": "Vehicle make:"},
    "Модель:": {"uk": "Модель:", "en": "Model:"},
    "Год выпуска:": {"uk": "Рік випуску:", "en": "Year:"},
    "Пробег:": {"uk": "Пробіг:", "en": "Mileage:"},
    "Тип топлива:": {"uk": "Тип пального:", "en": "Fuel type:"},
    "Объём двигателя:": {"uk": "Об’єм двигуна:", "en": "Engine size:"},
    "Коробка передач:": {"uk": "Коробка передач:", "en": "Transmission:"},
    "Привод:": {"uk": "Привід:", "en": "Drivetrain:"},
    "Загружаем справочники AUTO.RIA...": {"uk": "Завантажуємо довідники AUTO.RIA...", "en": "Loading AUTO.RIA reference data..."},
    "Справочники загружены. Выберите марку автомобиля.": {"uk": "Довідники завантажено. Виберіть марку автомобіля.", "en": "Reference data loaded. Select a vehicle make."},
    "Загружаем модели выбранной марки...": {"uk": "Завантажуємо моделі вибраної марки...", "en": "Loading models for the selected make..."},
    "Загрузка моделей...": {"uk": "Завантаження моделей...", "en": "Loading models..."},
    "Выберите модель и заполните параметры автомобиля.": {"uk": "Виберіть модель і заповніть параметри автомобіля.", "en": "Select a model and fill in the vehicle details."},
    "Ошибка загрузки справочников.": {"uk": "Помилка завантаження довідників.", "en": "Failed to load reference data."},
    "Ошибка AUTO.RIA": {"uk": "Помилка AUTO.RIA", "en": "AUTO.RIA error"},
    "Не удалось загрузить данные:\n\n": {"uk": "Не вдалося завантажити дані:\n\n", "en": "Could not load data:\n\n"},
    "Не выбрана модель": {"uk": "Модель не вибрано", "en": "No model selected"},
    "Выберите марку и модель автомобиля.": {"uk": "Виберіть марку та модель автомобіля.", "en": "Select a vehicle make and model."},
    "Поиск электромобилей": {"uk": "Пошук електромобілів", "en": "Search electric vehicles"},
    "Выберите параметры электромобиля для анализа рынка": {"uk": "Виберіть параметри електромобіля для аналізу ринку", "en": "Choose electric vehicle parameters for market analysis"},
    "Загружаем справочники AUTO.RIA...": {"uk": "Завантажуємо довідники AUTO.RIA...", "en": "Loading AUTO.RIA reference data..."},
    "Загружаем марки AUTO.RIA...": {"uk": "Завантажуємо марки AUTO.RIA...", "en": "Loading AUTO.RIA makes..."},
    "Выберите марку электромобиля.": {"uk": "Виберіть марку електромобіля.", "en": "Select an electric vehicle make."},
    "Выберите модель и укажите год и пробег.": {"uk": "Виберіть модель і вкажіть рік та пробіг.", "en": "Select a model and specify year and mileage."},
    "Изображение muscle_car.png не найдено": {"uk": "Зображення muscle_car.png не знайдено", "en": "muscle_car.png image not found"},
    "Поиск электромобилей и анализ\nих рыночной стоимости": {"uk": "Пошук електромобілів та аналіз\nїхньої ринкової вартості", "en": "Search electric vehicles and analyze\ntheir market value"},
    "Поиск автомобилей с бензиновыми,\nдизельными и гибридными двигателями": {"uk": "Пошук автомобілів із бензиновими,\nдизельними та гібридними двигунами", "en": "Search petrol, diesel and hybrid\nvehicles"},
    "AUTO.RIA CAR PRICE ANALYZER   •   AI MARKET ANALYSIS": {"uk": "AUTO.RIA АНАЛІЗ ЦІН   •   АНАЛІЗ РИНКУ ЗА ДОПОМОГОЮ ШІ", "en": "AUTO.RIA CAR PRICE ANALYZER   •   AI MARKET ANALYSIS"},
    "Результаты поиска": {"uk": "Результати пошуку", "en": "Search results"},
    "Ожидание результатов": {"uk": "Очікування результатів", "en": "Waiting for results"},
    "Здесь появятся результаты поиска AUTO.RIA": {"uk": "Тут з’являться результати пошуку AUTO.RIA", "en": "AUTO.RIA search results will appear here"},
    "Найденные автомобили": {"uk": "Знайдені автомобілі", "en": "Found vehicles"},
    "Анализ рынка от GPT": {"uk": "Аналіз ринку від GPT", "en": "Market analysis by GPT"},
    "Здесь появится анализ найденных автомобилей.": {"uk": "Тут з’явиться аналіз знайдених автомобілів.", "en": "The analysis of found vehicles will appear here."},
    "Открыть объявление": {"uk": "Відкрити оголошення", "en": "Open listing"},
    "Поиск...": {"uk": "Пошук...", "en": "Searching..."},
    "Выполняется поиск автомобилей и анализ рынка...": {"uk": "Виконується пошук автомобілів та аналіз ринку...", "en": "Searching for vehicles and analyzing the market..."},
    "Автомобили не найдены.": {"uk": "Автомобілі не знайдено.", "en": "No vehicles found."},
    "Нет данных для анализа.": {"uk": "Немає даних для аналізу.", "en": "No data available for analysis."},
    "Не удалось выполнить анализ GPT.\n\n": {"uk": "Не вдалося виконати аналіз GPT.\n\n", "en": "GPT analysis failed.\n\n"},
    "Персонализация": {"uk": "Персоналізація", "en": "Personalization"},
    "Выберите оформление приложения": {"uk": "Виберіть оформлення застосунку", "en": "Choose application appearance"},
    "Предпросмотр": {"uk": "Попередній перегляд", "en": "Preview"},
    "Выберите тему для применения": {"uk": "Виберіть тему для застосування", "en": "Choose a theme"},
    "Изображения не найдены.\nПроверьте папку assets/backgrounds.": {"uk": "Зображення не знайдено.\nПеревірте папку assets/backgrounds.", "en": "Images not found.\nCheck the assets/backgrounds folder."},
    "Размытие фона": {"uk": "Розмиття фону", "en": "Background blur"},
    "Затемнение фона": {"uk": "Затемнення фону", "en": "Background dimming"},
    "Готово": {"uk": "Готово", "en": "Done"},
    "Нет изображения": {"uk": "Немає зображення", "en": "No image"},
    "Выбрано: Стиль ": {"uk": "Вибрано: Стиль ", "en": "Selected: Style "},
    "Стиль ": {"uk": "Стиль ", "en": "Style "},
    "✓ Выбрано": {"uk": "✓ Вибрано", "en": "✓ Selected"},
    "Поиск уже выполняется": {"uk": "Пошук уже виконується", "en": "Search already in progress"},
    "Дождитесь завершения текущего поиска.": {"uk": "Дочекайтеся завершення поточного пошуку.", "en": "Please wait for the current search to finish."},
    "Произошла ошибка при выполнении поиска.": {"uk": "Під час пошуку сталася помилка.", "en": "An error occurred while searching."},
    "Ошибка поиска": {"uk": "Помилка пошуку", "en": "Search error"},
    "Загружено: ": {"uk": "Завантажено: ", "en": "Loaded: "},
    " из ": {"uk": " із ", "en": " of "},
    "Не удалось загрузить: ": {"uk": "Не вдалося завантажити: ", "en": "Failed to load: "},
    "Год: ": {"uk": "Рік: ", "en": "Year: "},
    "Пробег: ": {"uk": "Пробіг: ", "en": "Mileage: "},
    "Топливо: ": {"uk": "Пальне: ", "en": "Fuel: "},
    "Цена: $": {"uk": "Ціна: $", "en": "Price: $"},
    "Анализ рынка от GPT": {"uk": "Аналіз ринку від GPT", "en": "Market analysis by GPT"},
    "Здесь появится анализ найденных автомобилей.": {"uk": "Тут з’явиться аналіз знайдених автомобілів.", "en": "Analysis of found vehicles will appear here."},
    "Здесь появится аналитика GPT после завершения поиска.": {"uk": "Тут з’явиться аналітика GPT після завершення пошуку.", "en": "GPT analysis will appear here after the search is complete."},
    "Подготавливаем параметры поиска...": {"uk": "Готуємо параметри пошуку...", "en": "Preparing search parameters..."},
    "Ищем объявления на AUTO.RIA...": {"uk": "Шукаємо оголошення на AUTO.RIA...", "en": "Searching AUTO.RIA listings..."},
    "Найдено объявлений: ": {"uk": "Знайдено оголошень: ", "en": "Listings found: "},
    "Загружаем объявления: ": {"uk": "Завантажуємо оголошення: ", "en": "Loading listings: "},
    "Подготавливаем данные для GPT...": {"uk": "Готуємо дані для GPT...", "en": "Preparing data for GPT..."},
    "GPT анализирует найденные автомобили...": {"uk": "GPT аналізує знайдені автомобілі...", "en": "GPT is analyzing the found vehicles..."},
    "Не удалось загрузить подробности объявлений.": {"uk": "Не вдалося завантажити подробиці оголошень.", "en": "Could not load listing details."},
    "Не удалось загрузить: ": {"uk": "Не вдалося завантажити: ", "en": "Failed to load: "},
    "Ожидание результатов": {"uk": "Очікування результатів", "en": "Waiting for results"},
    " год": {"uk": " рік", "en": " year"},
    " км": {"uk": " км", "en": " km"},
    " л": {"uk": " л", "en": " L"},
}

class Localization(QObject):
    languageChanged = Signal(str)
    LANGUAGES = {"ru": "RU", "uk": "UA", "en": "EN"}

    def __init__(self):
        super().__init__()
        self.settings = QSettings("PetParsingAI", "ThemeSettings")
        self.language = self.settings.value("language", "ru")
        if self.language not in self.LANGUAGES:
            self.language = "ru"

    def set_language(self, language: str):
        if language not in self.LANGUAGES:
            return
        if language == self.language:
            return
        self.language = language
        self.settings.setValue("language", language)
        self.languageChanged.emit(language)

    def tr(self, text: str) -> str:
        if self.language == "ru":
            return text
        return TRANSLATIONS.get(text, {}).get(self.language, text)


def translate_text(text: str, language: str) -> str:
    if language == "ru":
        return text
    return TRANSLATIONS.get(text, {}).get(language, text)


def translate_widget_tree(root, language: str):
    """Переводит стандартные текстовые свойства всех дочерних Qt-виджетов."""
    from PySide6.QtWidgets import (
        QLabel, QPushButton, QToolButton, QComboBox, QSpinBox,
        QDoubleSpinBox, QLineEdit, QTextEdit, QPlainTextEdit,
        QGroupBox, QCheckBox, QRadioButton
    )

    reverse = {}
    for source, variants in TRANSLATIONS.items():
        reverse[source] = source
        for translated in variants.values():
            reverse[translated] = source

    def translated(value):
        source = reverse.get(value, value)
        return translate_text(source, language)

    widgets = [root] + root.findChildren(__import__('PySide6.QtWidgets', fromlist=['QWidget']).QWidget)
    for widget in widgets:
        if isinstance(widget, (QLabel, QPushButton, QToolButton, QCheckBox, QRadioButton, QGroupBox)):
            widget.setText(translated(widget.text()))
        elif isinstance(widget, QComboBox):
            for index in range(widget.count()):
                widget.setItemText(index, translated(widget.itemText(index)))
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.setSuffix(translated(widget.suffix()))
        elif isinstance(widget, QLineEdit):
            widget.setPlaceholderText(translated(widget.placeholderText()))
        elif isinstance(widget, (QTextEdit, QPlainTextEdit)):
            widget.setPlaceholderText(translated(widget.placeholderText()))

    if hasattr(root, "windowTitle"):
        root.setWindowTitle(translated(root.windowTitle()))

def tr(text: str) -> str:
    settings = QSettings("PetParsingAI", "ThemeSettings")
    language = settings.value("language", "ru")
    return translate_text(text, language)
