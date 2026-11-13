import logging
import requests
from backend.config import get_auto_ria_api_key

API_KEY = get_auto_ria_api_key()

logging.basicConfig(filename="app.log", level=logging.ERROR,
                    format="%(asctime)s | %(levelname)s | %(message)s", encoding="utf-8")
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

def get_fuel_types():
    url = "https://developers.ria.com/auto/type"
    return api_get_json(url, {"api_key": API_KEY})

def get_gearboxes():
    url = "https://developers.ria.com/auto/categories/1/gearboxes"
    return api_get_json(url, {"api_key": API_KEY})

def get_drive_types():
    url = "https://developers.ria.com/auto/categories/1/driverTypes"
    return api_get_json(url, {"api_key": API_KEY})

def search_cars(
        brand_id,
        model_id,
        countpage=100,
        page=0,
        year_from=None,
        year_to=None,
        fuel_id=None,
        gearbox_id=None,
        drive_id=None,
        engine_from=None,
        engine_to=None,
        mileage_from_km=None,
        mileage_to_km=None,
        battery_capacity_from_kwh=None,
        battery_capacity_to_kwh=None,
        range_from_km = None,
        range_to_km = None):

    url = "https://developers.ria.com/auto/search"
    params = {
        "api_key": API_KEY,
        "category_id": 1,
        "marka_id[0]": brand_id,
        "model_id[0]": model_id,
        "countpage": countpage,
        "page": page
    }
    if year_from is not None:
        params["s_yers[0]"] = year_from

    if year_to is not None:
        params["po_yers[0]"] = year_to

    if fuel_id is not None:
        params["type[0]"] = fuel_id

    if gearbox_id is not None:
        params["gearbox[0]"] = gearbox_id

    if drive_id is not None:
        params["drive_id[0]"] = drive_id

    if engine_from is not None:
        params["engineVolumeFrom[0]"] = engine_from

    if engine_to is not None:
        params["engineVolumeTo[0]"] = engine_to

    if mileage_from_km is not None and mileage_to_km is not None:
        params["raceFrom"] = mileage_from_km // 1000
        params["raceTo"] = mileage_to_km // 1000
    elif mileage_from_km is not None or mileage_to_km is not None:
        raise ValueError("Для фильтра пробега укажи обе границы")

    # Фильтр ёмкости батареи для электромобилей.
    # Имена параметров взяты из URL поиска AUTO.RIA.
    # if battery_capacity_from_kwh is not None and battery_capacity_to_kwh is not None:
    #     params["all[0].any[0].accumulator_capacity[0]"] = battery_capacity_from_kwh
    #     params["all[0].any[0].accumulator_capacity[1]"] = battery_capacity_to_kwh
    # elif battery_capacity_from_kwh is not None or battery_capacity_to_kwh is not None:
    #     raise ValueError("Для фильтра ёмкости батареи укажи обе границы")

    # # Фильтр запаса хода электромобиля
    # if range_from_km is not None and range_to_km is not None:
    #     params["all[0].any[0].power_reserve[0]"] = range_from_km
    #     params["all[0].any[0].power_reserve[1]"] = range_to_km
    # elif range_from_km is not None or range_to_km is not None:
    #     raise ValueError("Для фильтра запаса хода укажи обе границы")

    return api_get_json(url, params)

def get_car_details(car_id):
    url = "https://developers.ria.com/auto/info"
    params = {
        "api_key": API_KEY,
        "auto_id": car_id,
    }
    return api_get_json(url, params)