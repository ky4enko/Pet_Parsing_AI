from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from backend.schemas.car import SearchCarRead, SearchCarResult
from typing import Literal

class SearchRequest(BaseModel):
    car_type: str

    brand_id: int
    model_id: int

    make: str
    model: str

    year: int
    mileage: int

    fuel_id: int | None = None
    fuel: str

    engine_volume: float | None = None

    gearbox_id: int | None = None
    gearbox: str | None = None

    drive_id: int | None = None
    drive: str | None = None

    language: Literal["ru", "uk", "en"] = "ru"

class SearchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    status: str

    search_params: dict

    gpt_analysis: str | None = None
    gpt_model: str | None = None

    cars: list[SearchCarRead] = Field(default_factory=list)

class SearchResult(BaseModel):
    search_id: int
    cars: list[SearchCarResult] = Field(default_factory=list)
    analysis: str
    analysis_error: str | None = None
    total_found: int
    failed_count: int
    json_path: str | None = None
    analysis_path: str | None = None
    status: str

class SearchHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    status: str
    search_params: dict
    gpt_analysis: str | None = None
    gpt_model: str | None = None