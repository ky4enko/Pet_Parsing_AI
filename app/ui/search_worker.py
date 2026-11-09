import logging
import re
from datetime import datetime
from pathlib import Path

import requests
from PySide6.QtCore import QThread, Signal

from service.ria_client import search_cars, get_car_details
from service.car_parser import parse_car

from app.localization import translate_text

from ai_models.gpt import (
    build_market_payload,
    save_market_payload,
    analyze_market,
)


class SearchWorker(QThread):
    progressChanged = Signal(str)
    resultReady = Signal(dict)
    errorOccurred = Signal(str)

    def __init__(self, search_data, language="ru"):
        super().__init__()
        self.search_data = search_data
        self.language = language

    def emit_progress(self, message):
        from PySide6.QtCore import QSettings
        self.language = QSettings("PetParsingAI", "ThemeSettings").value("language", self.language)
        if message.startswith("Найдено объявлений: "):
            message = translate_text("Найдено объявлений: ", self.language) + message.split(": ", 1)[1]
        elif message.startswith("Загружаем объявления: "):
            message = translate_text("Загружаем объявления: ", self.language) + message.split(": ", 1)[1]
        else:
            message = translate_text(message, self.language)
        self.progressChanged.emit(message)

    def run(self):
        try:
            data = self.search_data

            self.emit_progress("Подготавливаем параметры поиска...")

            # Формируем фильтры AUTO.RIA
            year = data["year"]
            mileage = data["mileage"]

            filters = {
                "year_from": year - 3,
                "year_to": year + 3,
                "mileage_from_km": max(0, mileage - 15_000),
                "mileage_to_km": mileage + 15_000,
            }

            if data["car_type"] == "combustion":
                engine = data["engine_volume"]

                filters.update({
                    "fuel_id": data["fuel_id"],
                    "gearbox_id": data["gearbox_id"],
                    "drive_id": data["drive_id"],
                    "engine_from": max(0.1, engine - 0.5),
                    "engine_to": engine + 0.5,
                })
            else:
                if data.get("fuel_id") is not None:
                    filters["fuel_id"] = data["fuel_id"]

            # Получаем ID объявлений
            self.emit_progress("Ищем объявления на AUTO.RIA...")

            car_ids = []
            seen_ids = set()

            page = 0
            countpage = 100

            while True:
                if self.isInterruptionRequested():
                    return

                response = search_cars(
                    data["brand_id"],
                    data["model_id"],
                    countpage=countpage,
                    page=page,
                    **filters,
                )

                ids = response["result"]["search_result"]["ids"]

                if not ids:
                    break

                for car_id in ids:
                    if car_id not in seen_ids:
                        seen_ids.add(car_id)
                        car_ids.append(car_id)

                self.emit_progress(f"Найдено объявлений: {len(car_ids)}")

                if len(ids) < countpage:
                    break

                page += 1

            if not car_ids:
                self.resultReady.emit({
                    "cars": [],
                    "analysis": "",
                    "analysis_error": None,
                    "total_found": 0,
                    "failed_count": 0,
                    "json_path": None,
                })
                return

            # Загружаем подробности объявлений
            found_cars = []
            failed_ids = []

            for index, car_id in enumerate(car_ids, start=1):
                if self.isInterruptionRequested():
                    return

                self.emit_progress(f"Загружаем объявления: {index}/{len(car_ids)}")

                try:
                    car_data = get_car_details(car_id)

                    car = parse_car(
                        car_data,
                        car_id,
                        data["car_type"]
                    )

                    if car is not None:
                        found_cars.append(car)
                    else:
                        failed_ids.append(car_id)

                except (
                    requests.RequestException,
                    KeyError,
                    TypeError,
                    ValueError,
                ):
                    logging.exception(
                        "Ошибка обработки автомобиля ID %s",
                        car_id
                    )
                    failed_ids.append(car_id)

            if not found_cars:
                self.resultReady.emit({
                    "cars": [],
                    "analysis": "",
                    "analysis_error": "Не удалось загрузить подробности объявлений.",
                    "total_found": len(car_ids),
                    "failed_count": len(failed_ids),
                    "json_path": None,
                })
                return

            # Подготавливаем информацию о поиске
            search_info = {
                "car_type": data["car_type"],
                "make": data["make"],
                "model": data["model"],
                "year_from": filters["year_from"],
                "year_to": filters["year_to"],
                "mileage_from_km": filters["mileage_from_km"],
                "mileage_to_km": filters["mileage_to_km"],
                "fuel": data["fuel"],
            }

            if data["car_type"] == "combustion":
                search_info.update({
                    "engine_from": filters["engine_from"],
                    "engine_to": filters["engine_to"],
                    "gearbox": data["gearbox"],
                    "drive": data["drive"],
                })

            # Сохраняем объявления в папку search
            self.emit_progress("Подготавливаем данные для GPT...")

            payload = build_market_payload(
                search_info,
                found_cars
            )

            car_name = f"{data['make']}_{data['model']}"

            if data["car_type"] == "combustion":
                car_name += f"_{data['engine_volume']}"

            car_name = re.sub(
                r"[^\w.-]+",
                "_",
                car_name,
                flags=re.UNICODE
            ).strip("._")

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            filename = f"{car_name}_{timestamp}.json"
            json_path = Path("search") / filename

            saved_path = save_market_payload(
                payload,
                path=str(json_path)
            )

            # Запускаем GPT
            analysis = ""
            analysis_error = None

            self.emit_progress("GPT анализирует найденные автомобили...")

            try:
                from PySide6.QtCore import QSettings
                self.language = QSettings("PetParsingAI", "ThemeSettings").value("language", self.language)
                analysis = analyze_market(payload, language=self.language)

            except Exception as error:
                logging.exception("Ошибка GPT-анализа")
                analysis_error = str(error)

            # Передаём результат интерфейсу
            self.resultReady.emit({
                "cars": found_cars,
                "analysis": analysis,
                "analysis_error": analysis_error,
                "total_found": len(car_ids),
                "failed_count": len(failed_ids),
                "json_path": str(saved_path),
            })

        except Exception as error:
            logging.exception("Ошибка выполнения поиска")

            self.errorOccurred.emit(str(error))