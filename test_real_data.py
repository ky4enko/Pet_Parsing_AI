import json

from service.car_parser import parse_car


# Загружаем реальные данные
with open("cars_large_sample.json", "r", encoding="utf-8") as file:
    data = json.load(file)


cars = []

for item in data:
    car_id = item.get("autoData", {}).get("autoId")

    car = parse_car(item, car_id)
    cars.append(car)

    print("\n-------------------------")
    print(f"ID: {car.car_id}")
    print(f"Автомобиль: {car.make} {car.model}")
    print(f"Год: {car.year}")
    print(f"Пробег: {car.mileage_km}")
    print(f"Топливо: {car.fuel_name}")
    print(f"Объём двигателя: {car.engine_volume_l}")
    print(f"Коробка: {car.gearbox}")
    print(f"Привод: {car.drive_type}")
    print(f"Цена USD: {car.price_usd}")
    print(f"Модификация: {car.modification_name}")

print("\nВсего обработано:", len(cars))

from service.car_filter import CarFilter

# Первое объявление используем как целевой автомобиль
target = cars[0]

print("\nЦелевой автомобиль:")
print(target.make, target.model)
print("Год:", target.year)
print("Пробег:", target.mileage_km)

# Фильтруем похожие автомобили
filtered_cars = (
    CarFilter(cars)
    .filter_by_year(target.year)
    .filter_by_mileage(target.mileage_km)
    .filter_by_fuel(target.fuel_name.split(",")[0].strip())
    .filter_by_engine_volume(target.engine_volume_l)
    .filter_by_gearbox(target.gearbox)
    .filter_by_drive_type(target.drive_type)
    .get_results()
)

print("\nПохожие автомобили:")

for car in filtered_cars:
    print(
        f"ID: {car.car_id} | "
        f"{car.make} {car.model} | "
        f"{car.year} | "
        f"{car.mileage_km} км | "
        f"${car.price_usd}"
    )

print("\nНайдено похожих автомобилей:", len(filtered_cars))