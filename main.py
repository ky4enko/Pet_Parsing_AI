import logging
import requests
import re
from datetime import datetime
from service.ria_client import (
    get_marks,
    get_models,
    get_fuel_types,
    get_gearboxes,
    get_drive_types,
    search_cars,
    get_car_details,
)

from service.car_parser import parse_car

from ai_models.gpt import (
    build_market_payload,
    save_market_payload,
    analyze_market,
)


logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)


# --------------------------------------------------
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# --------------------------------------------------

def find_item_id(items, name):
    for item in items:
        if item.get("name", "").strip().casefold() == name.strip().casefold():
            return item.get("value")

    return None


def input_reference(title, items):
    print(f"\n{title}:")

    for item in items:
        print(f"- {item.get('name')}")

    while True:
        name = input("\nВведите значение: ").strip()
        item_id = find_item_id(items, name)

        if item_id is not None:
            return name, item_id

        print("Такого значения нет в справочнике. Попробуйте ещё раз.")


def input_int(prompt, minimum=0):
    while True:
        try:
            value = int(input(prompt))

            if value < minimum:
                print(f"Значение должно быть не меньше {minimum}.")
                continue

            return value

        except ValueError:
            print("Введите целое число.")


def input_float(prompt, minimum=0):
    while True:
        try:
            value = float(input(prompt).replace(",", "."))

            if value < minimum:
                print(f"Значение должно быть не меньше {minimum}.")
                continue

            return value

        except ValueError:
            print("Введите число.")


def input_car_type():
    print("\nВыберите тип автомобиля:")
    print("1. ДВС / гибрид")
    print("2. Электромобиль")

    while True:
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            return "combustion"

        if choice == "2":
            return "electric"

        print("Введите 1 или 2.")

def create_search_filename(make, model, car_type, engine_volume=None):
    """Создаёт имя файла поиска на основе автомобиля."""

    if car_type == "combustion":
        car_name = f"{make}_{model}_{engine_volume}"
    else:
        car_name = f"{make}_{model}"

    # Убираем недопустимые символы из имени файла.
    car_name = re.sub(r"[^\w.-]+", "_", car_name, flags=re.UNICODE)
    car_name = car_name.strip("._")

    # Добавляем дату и время, чтобы не перезаписывать предыдущие поиски.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{car_name}_{timestamp}.json"

# ПОИСК: ВСЕ КРИТЕРИИ ПЕРЕДАЮТСЯ AUTO.RIA
def collect_car_ids(brand_id, model_id, **filters):
    all_ids = []
    seen_ids = set()

    page = 0
    countpage = 100

    while True:
        data = search_cars(
            brand_id,
            model_id,
            countpage=countpage,
            page=page,
            **filters,
        )

        ids = data["result"]["search_result"]["ids"]

        if not ids:
            break

        for car_id in ids:
            if car_id not in seen_ids:
                seen_ids.add(car_id)
                all_ids.append(car_id)

        print(f"Страница {page + 1}: получено {len(ids)} объявлений")

        if len(ids) < countpage:
            break

        page += 1

    return all_ids


def collect_car_details(car_ids, car_type):
    """Загружает карточки. Не фильтрует и не перепроверяет критерии поиска."""

    loaded_cars = []
    failed_ids = []

    for index, car_id in enumerate(car_ids, start=1):
        print(
            f"\rЗагрузка автомобилей: {index}/{len(car_ids)}",
            end=""
        )

        try:
            car_data = get_car_details(car_id)
            car = parse_car(car_data, car_id, car_type)

            if car is None:
                failed_ids.append(car_id)
            else:
                loaded_cars.append(car)

        except requests.RequestException:
            logging.exception(
                "Ошибка запроса автомобиля ID %s",
                car_id
            )
            failed_ids.append(car_id)

        except (KeyError, TypeError, ValueError):
            logging.exception(
                "Ошибка обработки автомобиля ID %s",
                car_id
            )
            failed_ids.append(car_id)

    print()

    return loaded_cars, failed_ids


def print_cars(cars, car_type):
    """Выводит найденные автомобили с учётом выбранного типа."""

    for car in cars:
        print("\n------------------------------")

        print(f"Автомобиль: {car.make} {car.model}")
        print(f"Год: {car.year}")
        print(f"Пробег: {car.mileage_km} км")

        print(f"ID: {car.car_id}")

        if car_type == "electric":
            if car.modification_name:
                print(f"Модификация: {car.modification_name}")

        else:
            print(f"Топливо: {car.fuel_name}")
            print(f"Объём двигателя: {car.engine_volume_l} л")
            print(f"Модификация: {car.modification_name}")
            print(f"Коробка: {car.gearbox}")
            print(f"Привод: {car.drive_type}")

        print(f"Цена USD: {car.price_usd}")
        print(f"Цена UAH: {car.price_uah}")
        print(f"Ссылка: {car.url}")


# ОСНОВНАЯ ПРОГРАММА
def main():
    print("=" * 45)
    print("       AUTO.RIA CAR PRICE ANALYZER")
    print("=" * 45)

    try:
        car_type = input_car_type()

        print("\nЗагружаем справочники AUTO.RIA...")

        marks = get_marks()
        fuel_types = get_fuel_types()

        if car_type == "combustion":
            gearboxes = get_gearboxes()
            drive_types = get_drive_types()

        make, brand_id = input_reference("Марки автомобилей", marks)

        models = get_models(brand_id)
        model, model_id = input_reference("Модели автомобилей", models)

        year = input_int("\nГод выпуска: ", minimum=1900)
        mileage = input_int("Пробег (км): ")

        search_filters = {
            "year_from": year - 3,
            "year_to": year + 3,

            # Диапазон пробега: выбранное значение ±15 000 км.
            "mileage_from_km": max(0, mileage - 15_000),
            "mileage_to_km": mileage + 15_000,
        }

        if car_type == "combustion":
            fuel_name, fuel_id = input_reference(
                "Типы топлива",
                fuel_types
            )

            engine_volume = input_float(
                "Объём двигателя (л): ",
                minimum=0.1
            )

            gearbox_name, gearbox_id = input_reference(
                "Типы коробок передач",
                gearboxes
            )

            drive_name, drive_id = input_reference(
                "Типы привода",
                drive_types
            )

            search_filters.update({
                "fuel_id": fuel_id,
                "gearbox_id": gearbox_id,
                "drive_id": drive_id,
                "engine_from": max(0.1, engine_volume - 0.5),
                "engine_to": engine_volume + 0.5,
            })

        else:
            # Для электромобилей используем только год, пробег и тип топлива.
            fuel_name = "Електро"
            fuel_id = find_item_id(fuel_types, fuel_name)

            if fuel_id is None:
                raise ValueError(
                    "В справочнике AUTO.RIA не найден тип топлива 'Електро'."
                )

        print("\n" + "=" * 45)
        print("ПАРАМЕТРЫ СЕРВЕРНОГО ПОИСКА")
        print("=" * 45)

        print(f"Автомобиль: {make} {model}")

        print(
            f"Год: {search_filters['year_from']}–"
            f"{search_filters['year_to']}"
        )

        print(
            f"Пробег: {search_filters['mileage_from_km']}–"
            f"{search_filters['mileage_to_km']} км"
        )

        print(f"Топливо: {fuel_name}")

        if car_type == "combustion":
            print(
                f"Двигатель: {search_filters['engine_from']}–"
                f"{search_filters['engine_to']} л"
            )

            print(f"Коробка: {gearbox_name}")
            print(f"Привод: {drive_name}")

        else:
            print("Дополнительные фильтры: не используются")

        print("\nИщем объявления на AUTO.RIA...")

        car_ids = collect_car_ids(
            brand_id,
            model_id,
            **search_filters
        )

        print(f"\nНайдено сервером AUTO.RIA: {len(car_ids)}")

        if not car_ids:
            print("По заданным параметрам ничего не найдено.")
            return

        print("\nЗагружаем подробности найденных объявлений...")

        found_cars, failed_ids = collect_car_details(
            car_ids,
            car_type
        )

        print("\n" + "=" * 45)
        print("РЕЗУЛЬТАТЫ ПОИСКА")
        print("=" * 45)

        print(f"Найдено сервером: {len(car_ids)}")
        print(f"Подробности загружены: {len(found_cars)}")
        print(f"Не удалось загрузить/обработать: {len(failed_ids)}")

        if found_cars:
            print("\n--- ОБЪЯВЛЕНИЯ, ОТОБРАННЫЕ AUTO.RIA ---")
            print_cars(found_cars, car_type)

        if failed_ids:
            print("\n--- НЕ УДАЛОСЬ ЗАГРУЗИТЬ ПОДРОБНОСТИ ---")

            for car_id in failed_ids:
                print(f"ID: {car_id}")

        # GPT: АНАЛИЗ РЫНКА
        if found_cars:
            search_info = {
                "car_type": car_type,
                "make": make,
                "model": model,
                "year_from": search_filters["year_from"],
                "year_to": search_filters["year_to"],
                "mileage_from_km": search_filters["mileage_from_km"],
                "mileage_to_km": search_filters["mileage_to_km"],
                "fuel": fuel_name,
            }

            if car_type == "combustion":
                search_info.update({
                    "engine_from": search_filters["engine_from"],
                    "engine_to": search_filters["engine_to"],
                    "gearbox": gearbox_name,
                    "drive": drive_name,
                })

            try:
                print("\nФормируем JSON и отправляем объявления в GPT...")

                payload = build_market_payload(
                    search_info,
                    found_cars
                )

                # Создаём название файла на основе выбранного автомобиля.
                if car_type == "combustion":
                    filename = create_search_filename(
                        make,
                        model,
                        car_type,
                        engine_volume
                    )
                else:
                    filename = create_search_filename(
                        make,
                        model,
                        car_type
                    )

                # Все поиски сохраняются в отдельной папке search.
                search_path = f"search/{filename}"

                json_path = save_market_payload(
                    payload,
                    path=search_path
                )

                print(f"Объявления сохранены: {json_path}")

                print("\nОжидаем анализ GPT...")

                analysis = analyze_market(payload)

                print("\n" + "=" * 45)
                print("АНАЛИЗ РЫНКА ОТ GPT")
                print("=" * 45)

                print(analysis)

                print("\n" + "=" * 45)
                print("АНАЛИЗ ЗАВЕРШЁН")
                print("=" * 45)

                print("\n" + "=" * 45)
                print("АНАЛИЗ ЗАВЕРШЁН")
                print("=" * 45)

            except Exception:
                logging.exception("Ошибка GPT-анализа")

                print(
                    "\nНе удалось выполнить GPT-анализ. "
                    "Результаты парсинга сохранены в консоли и не потеряны. "
                    "Подробности ошибки записаны в app.log."
                )

    except requests.RequestException:
        logging.exception("Ошибка взаимодействия с AUTO.RIA API")

        print(
            "\nОшибка запроса к AUTO.RIA. "
            "Подробности записаны в app.log."
        )

    except (KeyError, TypeError, ValueError):
        logging.exception("Ошибка выполнения поиска")

        print(
            "\nОшибка обработки данных. "
            "Подробности записаны в app.log."
        )


if __name__ == "__main__":
    main()