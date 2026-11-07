import os
import requests
from dotenv import load_dotenv
import logging

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

def get_marks():
    url = "https://developers.ria.com/auto/categories/1/marks"
    return api_get_json(url, {"api_key": API_KEY})

def get_models(brand_id):
    url = f"https://developers.ria.com/auto/categories/1/marks/{brand_id}/models"
    return api_get_json(url, {"api_key": API_KEY})

def search_cars(brand_id, model_id, countpage = 10, page = 0):
    url = "https://developers.ria.com/auto/search"
    params = {
        "api_key": API_KEY,
        "category_id": 1,
        "marka_id[0]": brand_id,
        "model_id[0]": model_id,
        "countpage": countpage,
        "page": page
    }
    return api_get_json(url, params)

def get_car_details(car_id):
    url = "https://developers.ria.com/auto/info"
    params = {
        "api_key": API_KEY,
        "auto_id": car_id,
    }
    return api_get_json(url, params)