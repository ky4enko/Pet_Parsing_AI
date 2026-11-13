from pydantic import BaseModel, ConfigDict

class SearchCarRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    search_id: int
    car_id: int
    car_type: str

    make: str
    model: str

    year: int | None = None
    mileage_km: int | None = None

    gearbox: str | None = None
    drive_type: str | None = None

    price_usd: float | None = None
    price_uah: float | None = None

    modification_name: str | None = None
    url: str | None = None
    photo_url: str | None = None

    fuel_name: str | None = None
    engine_volume_l: float | None = None

    raw_data: dict | None = None

class SearchCarResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    car_id: int
    make: str
    model: str
    year: int | None = None
    mileage_km: int | None = None
    gearbox: str | None = None
    drive_type: str | None = None
    price_usd: float | None = None
    price_uah: float | None = None
    modification_name: str | None = None
    url: str | None = None
    photo_url: str | None = None
    fuel_name: str | None = None
    engine_volume_l: float | None = None
