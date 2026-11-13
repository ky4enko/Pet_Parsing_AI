import logging
from PySide6.QtCore import QThread, Signal, QSettings
from backend_client import BackendClient
from app.localization import translate_text

class SearchWorker(QThread):
    progressChanged = Signal(str)
    resultReady = Signal(dict)
    errorOccurred = Signal(str)

    def __init__(self, search_data, language="ru"):
        super().__init__()
        self.search_data = search_data
        self.language = language
        self.backend_client = BackendClient()

    def emit_progress(self, message):
        self.language = QSettings(
            "PetParsingAI",
            "ThemeSettings"
        ).value("language", self.language)
        message = translate_text(
            message,
            self.language)
        self.progressChanged.emit(message)

    def run(self):
        try:
            self.emit_progress("Выполняется поиск...")
            # Отправляем поиск на сервер
            result = self.backend_client.create_search(
                self.search_data,
                language=self.language)
            self.resultReady.emit(result)
        except Exception as error:
            logging.exception(
                "Ошибка выполнения поиска через Backend")
            self.errorOccurred.emit(str(error))
