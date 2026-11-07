import logging
import requests

from service.ria_client import (
    get_marks,
    get_models,
    search_cars,
    get_car_details
)
from service.car_parser import parse_car


def find_id_by_name(items, name):
    """Находит ID марки или модели по названию."""

    for item in items:
        if item.get("name") == name:
            return item.get("value")

    return None


def main():
    # 1. Получаем список марок
    marks = get_marks()

    # 2. Находим BMW
    brand_id = find_id_by_name(marks, "BMW")

    if brand_id is None:
        print("Марка BMW не найдена")
        return

    print("ID марки BMW:", brand_id)

    # 3. Получаем модели BMW
    models = get_models(brand_id)

    # 4. Находим BMW 3 Series
    model_id = find_id_by_name(models, "3 Series")

    if model_id is None:
        print("Модель BMW 3 Series не найдена")
        return

    print("ID модели:", model_id)

    # 5. Ищем объявления
    data = search_cars(brand_id, model_id, countpage=10, page=0)

    # 6. Получаем ID объявлений
    car_ids = data["result"]["search_result"]["ids"]

    print("Найдено объявлений:", len(car_ids))
    cars = []

    # 7. Получаем информацию об автомобилях
    for car_id in car_ids:
        try:
            car_data = get_car_details(car_id)

            # Преобразуем JSON в объект Car
            car = parse_car(car_data, car_id)
            print("Тип топлива:", car.fuel_name)
            print("Модификация:", car.modification_name)
            # Проверяем, соответствует ли автомобиль поисковому запросу
            if car.make != "BMW" or car.model != "3 Series":
                print(
                    f"Пропускаем неподходящий автомобиль: "
                    f"{car.make} {car.model}, ID: {car.car_id}"
                )
                continue
            cars.append(car)

            print("\n-------------------------")
            print("ID:", car.car_id)
            print("Марка:", car.make)
            print("Модель:", car.model)
            print("Цена UAH:", car.price_uah)
            print("Цена USD:", car.price_usd)
            print("Год:", car.year)
            print("Пробег:", car.mileage_km)
            print("Двигатель:", car.fuel_name)
            print("Объём двигателя:", car.engine_volume_l)
            print("Коробка:", car.gearbox)
            print("Привод:", car.drive_type)

        except requests.RequestException:
            logging.exception(
                "Ошибка запроса автомобиля ID %s", car_id
            )
            continue

        except (KeyError, TypeError, ValueError):
            logging.exception(
                "Ошибка обработки автомобиля ID %s", car_id
            )
            continue

    print("\n==============================")
    print("ИТОГИ СБОРА")
    print("==============================")
    print("Всего найдено объявлений:", len(car_ids))
    print("Подходящих автомобилей:", len(cars))

if __name__ == "__main__":
    main()
