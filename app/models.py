from dataclasses import dataclass

@dataclass
class Car:
    car_id: int
    make: str
    model: str

    #характеристики
    year: int | None = None
    mileage_km: int | None = None
    fuel_name: str | None = None
    engine_volume_l: float | None = None
    battery_capacity_kwh: float | None = None
    gearbox: str | None = None
    drive_type: str | None = None

    #цена
    price_usd: float | None = None
    price_uah: float | None = None

    #доп информация
    modification_name: str | None = None
    url: str | None = None