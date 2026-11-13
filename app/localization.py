"""Централизованная локализация интерфейса AUTO.RIA Analyzer."""
from PySide6.QtCore import QObject, QSettings, Signal

TRANSLATIONS = {
    "Главная": {"uk": "Головна", "en": "Home"},
    "ДВС / Гибрид": {"uk": "ДВЗ / Гібрид", "en": "ICE / Hybrid"},
    "Электромобили": {"uk": "Електромобілі", "en": "Electric vehicles"},
    "Результаты": {"uk": "Результати", "en": "Results"},
    "Открыты сохранённые результаты поиска.": {"uk": "Відкрито збережені результати пошуку.", "en": "Saved search results opened."},
    "История": {"uk": "Історія", "en": "History"},
    "История поисков": {"uk": "Історія пошуків", "en": "Search history"},
    "Ранее выполненные поиски и сохранённые результаты.": {"uk": "Раніше виконані пошуки та збережені результати.", "en": "Previous searches and saved results."},
    "Обновить": {"uk": "Оновити", "en": "Refresh"},
    "Загрузить ещё": {"uk": "Завантажити ще", "en": "Load more"},
    "Загружаем ещё записи...": {"uk": "Завантажуємо наступні записи...", "en": "Loading more records..."},
    "Поисков: ": {"uk": "Пошуків: ", "en": "Searches: "},
    "История недоступна": {"uk": "Історія недоступна", "en": "History unavailable"},
    "Загружаем историю поисков...": {"uk": "Завантажуємо історію пошуків...", "en": "Loading search history..."},
    "Не удалось загрузить историю.": {"uk": "Не вдалося завантажити історію.", "en": "Could not load search history."},
    "Пока нет сохранённых поисков. Начните поиск — он появится здесь.": {"uk": "Поки немає збережених пошуків. Почніть пошук — він з’явиться тут.", "en": "No saved searches yet. Run a search and it will appear here."},
    "История временно недоступна. Нажмите «Обновить», чтобы повторить запрос.": {"uk": "Історія тимчасово недоступна. Натисніть «Оновити», щоб повторити запит.", "en": "History is temporarily unavailable. Press “Refresh” to try again."},
    "Загружаем сохранённый поиск": {"uk": "Завантажуємо збережений пошук", "en": "Loading saved search"},
    "Не удалось открыть сохранённый поиск.": {"uk": "Не вдалося відкрити збережений пошук.", "en": "Could not open the saved search."},
    "Backend вернул некорректный формат истории.": {"uk": "Backend повернув некоректний формат історії.", "en": "Backend returned an invalid history format."},
    "Backend вернул некорректный формат поиска.": {"uk": "Backend повернув некоректний формат пошуку.", "en": "Backend returned an invalid search format."},
    "Завершён": {"uk": "Завершено", "en": "Completed"},
    "Ошибка": {"uk": "Помилка", "en": "Failed"},
    "В процессе": {"uk": "У процесі", "en": "In progress"},
    "Неизвестно": {"uk": "Невідомо", "en": "Unknown"},
    "Дата не указана": {"uk": "Дату не вказано", "en": "Date not specified"},
    "Электромобиль": {"uk": "Електромобіль", "en": "Electric vehicle"},
    "Поиск": {"uk": "Пошук", "en": "Search"},
    "Открыть": {"uk": "Відкрити", "en": "Open"},
    "Параметры не указаны": {"uk": "Параметри не вказано", "en": "No parameters specified"},
    "Год": {"uk": "Рік", "en": "Year"},
    "Пробег": {"uk": "Пробіг", "en": "Mileage"},
    "км": {"uk": "км", "en": "km"},
    "Двигатель": {"uk": "Двигун", "en": "Engine"},
    "л": {"uk": "л", "en": "L"},
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


# Додаткові переклади для динамічних і раніше пропущених елементів інтерфейсу.
TRANSLATIONS.update({'Объявления AUTO.RIA и аналитика рыночной стоимости': {'uk': 'Оголошення AUTO.RIA та аналітика ринкової вартості', 'en': 'AUTO.RIA listings and market value analysis'}, 'Загружено автомобилей': {'uk': 'Завантажено автомобілів', 'en': 'Vehicles loaded'}, 'Найдено объявлений': {'uk': 'Знайдено оголошень', 'en': 'Listings found'}, 'Не удалось загрузить': {'uk': 'Не вдалося завантажити', 'en': 'Failed to load'}, 'Оценка цен, сравнение объявлений и выводы': {'uk': 'Оцінка цін, порівняння оголошень і висновки', 'en': 'Price estimates, listing comparisons and insights'}, 'Фото AUTO.RIA': {'uk': 'Фото AUTO.RIA', 'en': 'AUTO.RIA photo'}, 'Характеристики не указаны': {'uk': 'Характеристики не вказані', 'en': 'Specifications not provided'}, 'Автомобиль': {'uk': 'Автомобіль', 'en': 'Vehicle'}, 'Цена не указана': {'uk': 'Ціну не вказано', 'en': 'Price not provided'}, 'Фото недоступно': {'uk': 'Фото недоступне', 'en': 'Photo unavailable'}, 'Поиск выполняется': {'uk': 'Пошук виконується', 'en': 'Search in progress'}, 'Выполняется поиск на Backend...': {'uk': 'Виконується пошук на Backend...', 'en': 'Searching via the backend...'}, 'Не удалось завершить поиск. Подробности в сообщении об ошибке.': {'uk': 'Не вдалося завершити пошук. Подробиці наведено в повідомленні про помилку.', 'en': 'Search could not be completed. See the error message for details.'}, 'Загружено': {'uk': 'Завантажено', 'en': 'Loaded'}, 'Поиск завершился с ошибкой при загрузке объявлений.': {'uk': 'Пошук завершився з помилкою під час завантаження оголошень.', 'en': 'Search failed while loading listings.'}, 'Поиск завершён. Получен ответ от Backend.': {'uk': 'Пошук завершено. Отримано відповідь від Backend.', 'en': 'Search completed. Response received from the backend.'}, 'Автомобили не найдены': {'uk': 'Автомобілі не знайдено', 'en': 'No vehicles found'}, 'Backend завершил поиск, но подходящих объявлений нет. Попробуйте изменить параметры поиска.': {'uk': 'Backend завершив пошук, але відповідних оголошень немає. Спробуйте змінити параметри пошуку.', 'en': 'The backend completed the search, but no matching listings were found. Try changing the search parameters.'}, 'GPT-анализ не запускался, потому что объявления не найдены.': {'uk': 'GPT-аналіз не запускався, оскільки оголошень не знайдено.', 'en': 'GPT analysis was not started because no listings were found.'}, 'Backend не вернул текст GPT-анализа.': {'uk': 'Backend не повернув текст GPT-аналізу.', 'en': 'The backend did not return GPT analysis text.'}, 'В справочнике AUTO.RIA не найдены марки из каталога электромобилей.': {'uk': 'У довіднику AUTO.RIA не знайдено марок із каталогу електромобілів.', 'en': 'No makes from the electric vehicle catalog were found in the AUTO.RIA reference data.'}, 'Не удалось определить тип топлива «Електро». Поиск временно недоступен.': {'uk': 'Не вдалося визначити тип пального «Електро». Пошук тимчасово недоступний.', 'en': 'Could not identify the “Electric” fuel type. Search is temporarily unavailable.'}, 'Для этой марки пока нет моделей, совпадающих с каталогом электромобилей.': {'uk': 'Для цієї марки поки немає моделей, що відповідають каталогу електромобілів.', 'en': 'There are currently no models for this make that match the electric vehicle catalog.'}, 'Не определён тип топлива': {'uk': 'Не визначено тип пального', 'en': 'Fuel type not identified'}, 'Не удалось определить ID топлива «Електро» в справочнике AUTO.RIA.': {'uk': 'Не вдалося визначити ID пального «Електро» в довіднику AUTO.RIA.', 'en': 'Could not identify the “Electric” fuel ID in the AUTO.RIA reference data.'}, 'Начните вводить марку...': {'uk': 'Почніть вводити марку...', 'en': 'Start typing a make...'}, 'Начните вводить модель...': {'uk': 'Почніть вводити модель...', 'en': 'Start typing a model...'}, 'Поиск ': {'uk': 'Пошук ', 'en': 'Search '}, 'Загружаем сохранённый поиск ': {'uk': 'Завантажуємо збережений пошук ', 'en': 'Loading saved search '}, 'На главную': {'uk': 'На головну', 'en': 'Home'}, 'Backend вернул автомобиль в неожиданном формате: ': {'uk': 'Backend повернув автомобіль у неочікуваному форматі: ', 'en': 'Backend returned a car in an unexpected format: '}, 'Backend вернул неожиданный формат ответа: ': {'uk': 'Backend повернув неочікуваний формат відповіді: ', 'en': 'Backend returned an unexpected response format: '}, 'Выполняется поиск...': {'uk': 'Виконується пошук...', 'en': 'Searching...'}})

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
        return translate_text(text, self.language)



def _resolve_translation(text: str):
    """Возвращает исходный ключ и хвост динамической строки, если ключ найден."""
    if not isinstance(text, str):
        return None

    # Сначала точное совпадение с исходной строкой или одним из переводов.
    for source, variants in TRANSLATIONS.items():
        if text == source or text in variants.values():
            return source, ""

    # Затем ищем самый длинный префикс для строк с динамическим окончанием:
    # например, «Поиск #14» или «Поисков: 20».
    matches = []
    for source, variants in TRANSLATIONS.items():
        prefixes = (source, *variants.values())
        for prefix in prefixes:
            if prefix and prefix[-1].isspace() and text.startswith(prefix):
                matches.append((len(prefix), source, text[len(prefix):]))

    if not matches:
        return None

    _, source, suffix = max(matches, key=lambda item: item[0])
    return source, suffix


def translate_text(text: str, language: str) -> str:
    """Переводит точные UI-строки и поддерживает динамические суффиксы."""
    if not isinstance(text, str):
        return text

    resolved = _resolve_translation(text)
    if resolved is None:
        return text

    source, suffix = resolved
    if language not in ("ru", "uk", "en"):
        return text

    translated = TRANSLATIONS.get(source, {}).get(language, source)
    return translated + suffix


def translate_widget_tree(root, language: str):
    """Переводит подписи, подсказки и плейсхолдеры во всём дереве Qt-виджетов."""
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import (
        QWidget,
        QLabel,
        QPushButton,
        QToolButton,
        QComboBox,
        QSpinBox,
        QDoubleSpinBox,
        QLineEdit,
        QTextEdit,
        QTextBrowser,
        QPlainTextEdit,
        QGroupBox,
        QCheckBox,
        QRadioButton,
    )

    widgets = [root] + root.findChildren(QWidget)

    for widget in widgets:
        if isinstance(
            widget,
            (QLabel, QPushButton, QToolButton, QCheckBox, QRadioButton, QGroupBox),
        ):
            widget.setText(translate_text(widget.text(), language))

        elif isinstance(widget, QComboBox):
            for index in range(widget.count()):
                widget.setItemText(
                    index,
                    translate_text(widget.itemText(index), language),
                )
            if widget.isEditable() and widget.lineEdit() is not None:
                widget.lineEdit().setPlaceholderText(
                    translate_text(widget.lineEdit().placeholderText(), language)
                )

        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.setSuffix(translate_text(widget.suffix(), language))

        elif isinstance(widget, QLineEdit):
            widget.setPlaceholderText(
                translate_text(widget.placeholderText(), language)
            )

        elif isinstance(widget, QTextBrowser):
            widget.setPlaceholderText(
                translate_text(widget.placeholderText(), language)
            )
            current_text = widget.toPlainText()
            # Переводим только известные UI-сообщения. Текст GPT-отчёта не меняем.
            if _resolve_translation(current_text) is not None:
                widget.setPlainText(translate_text(current_text, language))

        elif isinstance(widget, (QTextEdit, QPlainTextEdit)):
            widget.setPlaceholderText(
                translate_text(widget.placeholderText(), language)
            )

        tooltip = widget.toolTip()
        if tooltip:
            widget.setToolTip(translate_text(tooltip, language))

        title = widget.windowTitle()
        if title:
            widget.setWindowTitle(translate_text(title, language))

    # QAction не является QWidget, поэтому обрабатываем отдельно.
    for action in root.findChildren(QAction):
        action.setText(translate_text(action.text(), language))
        if action.toolTip():
            action.setToolTip(translate_text(action.toolTip(), language))


def tr(text: str) -> str:
    settings = QSettings("PetParsingAI", "ThemeSettings")
    language = settings.value("language", "ru")
    return translate_text(text, language)
