from fastapi import APIRouter
from backend.integrations.ria_client import (
    get_marks,
    get_models,
    get_fuel_types,
    get_gearboxes,
    get_drive_types,
)

router = APIRouter(
    prefix="/dictionaries",
    tags=["Dictionaries"]
)

@router.get("/marks")
def get_marks_list():
    return get_marks()

@router.get("/models")
def get_models_list(brand_id: int):
    return get_models(brand_id)

@router.get("/fuel-types")
def get_fuel_types_list():
    return get_fuel_types()


@router.get("/gearboxes")
def get_gearboxes_list():
    return get_gearboxes()


@router.get("/drive-types")
def get_drive_types_list():
    return get_drive_types()