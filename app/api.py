import os
import requests
from dotenv import load_dotenv
import logging
import json

logging.basicConfig(filename="app.log", level=logging.ERROR,
                    format="%(asctime)s | %(levelname)s | %(message)s", encoding="utf-8")

load_dotenv()
API_KEY = os.getenv("AUTO_RIA_API")
if not API_KEY:
    raise ValueError("API key not found in .env file")
# Wrapper error log
def api_get_json(url, params):
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as error:
        status_code =(error.response.status_code if error.response is not None else "Unknown")
        logging.error("HTTP-error. Code: %s", status_code)
        raise
    except requests.RequestException as error:
        logging.error("Request error. Type: %s", type(error).__name__)
        raise
    except ValueError:
        logging.error("JSON parsing error")
        raise


# 1. Получаем список марок автомобилей
url = "https://developers.ria.com/auto/categories/1/marks"

marks = api_get_json(url, {"api_key": API_KEY})

# 2. Находим ID марки BMW
brand_id = None

for mark in marks:
    if mark["name"] == "BMW":
        brand_id = mark["value"]
        break
print("ID марки BMW:", brand_id)

# 3. Получаем модели BMW
url = f"https://developers.ria.com/auto/categories/1/marks/{brand_id}/models"

models = api_get_json(url, {"api_key": API_KEY})

# 4. Ищем BMW 3 Series
model_id = None
for model in models:
    if model["name"] == "3 Series":
        model_id = model["value"]
        break
print("ID модели:", model_id)

# 5. Ищем объявления BMW 3 Series
url = "https://developers.ria.com/auto/search"
params = {
    "api_key": API_KEY,
    "category_id": 1,
    "marka_id[0]": brand_id,
    "model_id[0]": model_id,
    "countpage": 10,
    "page": 0
}

data = api_get_json(url, params)

# 6. Получаем ID найденных объявлений
car_ids = data["result"]["search_result"]["ids"]
print("Найдено объявлений:", len(car_ids))

# 7. Получаем подробную информацию по каждому автомобилю
for car_id in car_ids:
    try:
        url = "https://developers.ria.com/auto/info"

        params = {
            "api_key": API_KEY,
            "auto_id": car_id
        }

        car = api_get_json(url, params)
        auto = car["autoData"]

        print("\n-------------------------")
        print("ID:", car_id)
        print("Марка:", car.get("markName"))
        print("Модель:", car.get("modelName"))
        print("Цена UAH:", car.get("UAH"))
        print("Цена USD:", car.get("USD"))
        print("Год:", auto.get("year"))
        print("Пробег:", auto.get("race"))
        print("Двигатель:", auto.get("fuelName"))
        print("Коробка:", auto.get("gearboxName"))

    except requests.RequestException:
        continue

    except (KeyError, TypeError, ValueError) as error:
        logging.error(
            "Ошибка обработки автомобиля ID %s. Тип: %s",
            car_id,
            type(error).__name__)
        continue
