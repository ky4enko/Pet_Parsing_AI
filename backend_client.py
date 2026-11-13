import os
from pathlib import Path
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class BackendError(Exception):
    """Ошибка взаимодействия с Backend."""

class BackendClient:
    """Клиент для отправки HTTP-запросов к FastAPI."""

    def __init__(self, base_url=None):
        self.base_url = (
            base_url
            or os.getenv("BACKEND_BASE_URL")
            or "http://127.0.0.1:8000"
        ).rstrip("/")
        self.api_token = os.getenv("BACKEND_API_TOKEN")

        # Тайм-аут для обычных запросов
        self.timeout = (5, 20)

        # Поиск может занимать значительно больше времени
        self.search_timeout = (5, 600)

    def _request(
        self,
        method,
        endpoint,
        *,
        params=None,
        payload=None,
        timeout=None,
    ):
        """Выполняет HTTP-запрос и обрабатывает ошибки."""

        url = f"{self.base_url}{endpoint}"

        try:
            if not self.api_token:
                raise BackendError(
                    "Не задан BACKEND_API_TOKEN в файле .env."
                )

            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_token}"
                },
                timeout=timeout or self.timeout,
            )

        except requests.exceptions.Timeout as error:
            raise BackendError(
                "Время ожидания ответа Backend истекло."
            ) from error

        except requests.exceptions.ConnectionError as error:
            raise BackendError(
                f"Не удалось подключиться к Backend ({self.base_url}). "
                "Проверь, запущен ли Docker-контейнер."
            ) from error

        except requests.exceptions.RequestException as error:
            raise BackendError(
                f"Ошибка HTTP-запроса: {error}"
            ) from error

        if not response.ok:
            try:
                body = response.json()
                detail = body.get("detail", body)
            except ValueError:
                detail = response.text or "Нет описания ошибки"

            raise BackendError(
                f"Backend вернул HTTP {response.status_code}: {detail}"
            )

        try:
            return response.json()
        except ValueError as error:
            raise BackendError(
                "Backend вернул некорректный JSON."
            ) from error


    # ПРОВЕРКА СОЕДИНЕНИЯ
    def get_health(self):
        return self._request("GET", "/health")

    def get_db_health(self):
        return self._request("GET", "/health/db")

    # СПРАВОЧНИКИ AUTO.RIA
    def get_marks(self):
        return self._request(
            "GET",
            "/dictionaries/marks",
        )

    def get_models(self, brand_id):
        return self._request(
            "GET",
            "/dictionaries/models",
            params={"brand_id": brand_id},
        )

    def get_fuel_types(self):
        return self._request(
            "GET",
            "/dictionaries/fuel-types",
        )

    def get_gearboxes(self):
        return self._request(
            "GET",
            "/dictionaries/gearboxes",
        )

    def get_drive_types(self):
        return self._request(
            "GET",
            "/dictionaries/drive-types",
        )

    # ПОИСК АВТОМОБИЛЕЙ
    def create_search(self, search_data, language="ru"):
        payload = dict(search_data)
        payload["language"] = language

        return self._request(
            "POST",
            "/searches/",
            payload=payload,
            timeout=self.search_timeout,
        )

    # ИСТОРИЯ ПОИСКОВ
    def get_history(self, skip=0, limit=20):
        return self._request(
            "GET",
            "/history/",
            params={
                "skip": skip,
                "limit": limit,
            },
        )

    def get_search_details(self, search_id):
        return self._request(
            "GET",
            f"/history/{search_id}",
        )
