import re
from backend.entities.car import CombustionCar, ElectricCar

def parse_car(car_data: dict, car_id: int, car_type: str):
    if not isinstance(car_data, dict):
        raise TypeError("car_data должен быть словарем")

    auto = car_data.get("autoData") or {}

    if not isinstance(auto, dict):
        raise TypeError("autoData должен быть словарем")

    race_int = auto.get("raceInt")

    mileage_km = (
        int(race_int * 1000)
        if race_int is not None
        else None)

    # AUTO.RIA отдаёт ссылки на изображения в photoData.
    # В разных ответах API часть размеров может отсутствовать.
    photo_data = car_data.get("photoData") or {}
    photo_url = None
    if isinstance(photo_data, dict):
        for photo_key in ("seoLinkF", "seoLinkB", "seoLinkM", "seoLinkSX"):
            candidate = photo_data.get(photo_key)
            if isinstance(candidate, str) and candidate.startswith(("https://", "http://")):
                photo_url = candidate
                break
    elif isinstance(photo_data, list):
        # Некоторые ответы могут возвращать список объектов фотографий.
        for photo in photo_data:
            if not isinstance(photo, dict):
                continue
            for photo_key in ("seoLinkF", "seoLinkB", "seoLinkM", "url", "link"):
                candidate = photo.get(photo_key)
                if isinstance(candidate, str) and candidate.startswith(("https://", "http://")):
                    photo_url = candidate
                    break
            if photo_url:
                break

    common_data = {
        "car_id": car_id,
        "make": car_data.get("markName", ""),
        "model": car_data.get("modelName", ""),
        "year": auto.get("year"),
        "mileage_km": mileage_km,
        "gearbox": auto.get("gearboxName"),
        "drive_type": auto.get("driveName"),
        "price_usd": car_data.get("USD"),
        "price_uah": car_data.get("UAH"),
        "modification_name": auto.get("modificationName"),
        "url": car_data.get("linkToView"),
        "photo_url": photo_url,
    }

    if car_type == "electric":
        return ElectricCar(**common_data)
    elif car_type in ("combustion", "ice", "двс"):
        fuel_name = auto.get("fuelName")
        engine_volume_l = None
        if fuel_name:
            match = re.search(
                r"(\d+(?:[.,]\d+)?)\s*л\.?",
                fuel_name,
                re.IGNORECASE)
            if match:
                engine_volume_l = float(
                    match.group(1).replace(",", "."))
        return CombustionCar(
            **common_data,
            fuel_name=fuel_name,
            engine_volume_l=engine_volume_l)
    else:
        raise ValueError(f"Неизвестный тип автомобиля: {car_type}")