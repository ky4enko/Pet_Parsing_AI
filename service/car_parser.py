import re
from app.models import  Car

def parse_car(car_data : dict, car_id: int) -> Car:
    auto = car_data.get("autoData") or {}

    #пробег
    race_int = auto.get("raceInt")
    mileage_km = int(race_int * 1000) if race_int is not None else None

    #тип топлива
    fuel_name = auto.get("fuelName")

    #объем двигателя для двс
    engine_volume_l = None
    if fuel_name:
        volume_match = re.search(r"(\d+(?:[.,]\d+)?)\s*л", fuel_name)

        if volume_match:
            engine_volume_l = float(volume_match.group(1).replace(",", "."))


    #емкость акб для електро
    modification_name = auto.get("modificationName")
    battery_capacity_kwh = None
    if modification_name:
        battery_match = re.search(r"(\d+(?:[.,]\d+)?)\s*kWh", modification_name, re.IGNORECASE)
        if battery_match:
            battery_capacity_kwh = float(battery_match.group(1).replace(",", "."))

    return Car(
        car_id=car_id,
        make=car_data.get("markName", ""),
        model=car_data.get("modelName", ""),
        year=auto.get("year"),
        mileage_km=mileage_km,
        fuel_name=fuel_name,
        engine_volume_l=engine_volume_l,
        battery_capacity_kwh=battery_capacity_kwh,
        gearbox=auto.get("gearboxName"),
        drive_type=auto.get("driveName"),
        price_usd=car_data.get("USD"),
        price_uah=car_data.get("UAH"),
        modification_name=modification_name,
        url=car_data.get("linkToView")
    )