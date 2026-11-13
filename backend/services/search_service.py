import logging
import requests
from backend.integrations.ria_client import get_car_details, search_cars
from backend.services.car_parser import parse_car
from dataclasses import asdict
import re
from datetime import datetime
from pathlib import Path
from backend.config import SEARCH_DIR
from backend.services.market_analyzer import (
    build_market_payload,
    save_market_payload,
    analyze_market,
    save_analysis,
    DEFAULT_MODEL
    )
from sqlalchemy.orm import Session
from backend.repositories.search_repository import SearchRepository

class SearchService:
    def __init__(self, db: Session):
        self.repository = SearchRepository(db)
    @staticmethod
    def _build_filters(data: dict) -> dict:
        year = data["year"]
        mileage = data["mileage"]

        # Общие фильтры для всех автомобилей
        filters = {
            "year_from": year - 3,
            "year_to": year + 3,
            "mileage_from_km": max(0, mileage - 15_000),
            "mileage_to_km": mileage + 15_000,
        }
        # Дополнительные фильтры для автомобилей с ДВС
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
        return filters

    @staticmethod
    def _collect_car_ids(data: dict, filters: dict) -> list[int]:
        page = 0
        countpage = 100
        car_ids = []
        seen_ids = set()
        while True:
            response = search_cars(
                data["brand_id"],
                data["model_id"],
                countpage=countpage,
                page=page,
                **filters
            )
            page_ids = response["result"]["search_result"]["ids"]
            # Если объявлений больше нет — заканчиваем поиск
            if not page_ids:
                break
            # Добавляем только уникальные ID
            for car_id in page_ids:
                if car_id not in seen_ids:
                    seen_ids.add(car_id)
                    car_ids.append(car_id)
            # Если пришло меньше 100 объявлений,
            # значит, это последняя страница
            if len(page_ids) < countpage:
                break
            page += 1
        return car_ids

    @staticmethod
    def _load_cars(car_ids: list[int], car_type: str):
        found_cars = []
        failed_ids = []
        raw_data_by_id = {}
        for car_id in car_ids:
            try:
                car_data = get_car_details(car_id)
                car = parse_car(
                    car_data,
                    car_id,
                    car_type
                )
                if car is not None:
                    found_cars.append(car)
                    # Сохраняем исходный JSON объявления
                    raw_data_by_id[car_id] = car_data
                else:
                    failed_ids.append(car_id)
            except (
                    requests.RequestException,
                    KeyError,
                    TypeError,
                    ValueError
            ):
                logging.exception(
                    "Ошибка загрузки объявления %s",
                    car_id
                )
                failed_ids.append(car_id)
        return found_cars, failed_ids, raw_data_by_id

    @staticmethod
    def _build_search_info(data: dict, filters: dict) -> dict:
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
        return search_info

    @staticmethod
    def _prepare_cars_for_db(
            found_cars: list,
            car_type: str,
            raw_data_by_id: dict
    ) -> list[dict]:
        cars_data = []
        for car in found_cars:
            car_data = asdict(car)
            car_data["car_type"] = car_type
            # Добавляем исходный ответ AUTO.RIA
            car_data["raw_data"] = raw_data_by_id[car.car_id]
            cars_data.append(car_data)
        return cars_data

    @staticmethod
    def _build_market_payload(search_info: dict, found_cars: list) -> dict:
        return build_market_payload(search_info, found_cars)

    @staticmethod
    def _save_market_payload(payload: dict, data: dict) -> str:
        car_name = f"{data['make']}_{data['model']}"
        if data["car_type"] == "combustion":
            car_name += f"_{data['engine_volume']}"
        car_name = re.sub(
            r"[^\w.-]+",
            "_",
            car_name,
            flags=re.UNICODE
        ).strip("._")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{car_name}_{timestamp}.json"
        SEARCH_DIR.mkdir(parents=True, exist_ok=True)
        json_path = SEARCH_DIR / filename
        saved_path = save_market_payload(
            payload,
            path=str(json_path)
        )
        return str(saved_path)

    @staticmethod
    def _analyze_market(payload: dict, language: str = "ru") -> str:
        return analyze_market(
            payload,
            language=language
        )

    @staticmethod
    def _save_analysis(analysis: str, json_path: str) -> str:
        analysis_path = Path(json_path).with_suffix(".txt")
        save_analysis(
            analysis,
            path=analysis_path
        )
        return str(analysis_path)

    def search(self, data: dict, language: str = "ru") -> dict:
        # Создаём запись поиска в базе данных
        search_record = self.repository.create_search(data)
        search_id = search_record.id
        try:
            # 1. Формируем фильтры для AUTO.RIA
            filters = self._build_filters(data)

            # 2. Получаем ID объявлений
            car_ids = self._collect_car_ids(data, filters)

            # Если объявления не найдены
            if not car_ids:
                self.repository.complete_search(
                    search_id,
                    gpt_analysis="",
                    gpt_model=DEFAULT_MODEL,
                )
                return {
                    "search_id": search_id,
                    "cars": [],
                    "analysis": "",
                    "analysis_error": None,
                    "total_found": 0,
                    "failed_count": 0,
                    "json_path": None,
                    "analysis_path": None,
                    "status": "completed",
                }

            # 3. Загружаем подробности объявлений
            found_cars, failed_ids, raw_data_by_id = self._load_cars(
                car_ids,
                data["car_type"],
            )
            # Если не удалось обработать ни одного автомобиля
            if not found_cars:
                self.repository.fail_search(search_id)
                return {
                    "search_id": search_id,
                    "cars": [],
                    "analysis": "",
                    "analysis_error": "Не удалось загрузить подробности объявлений.",
                    "total_found": len(car_ids),
                    "failed_count": len(failed_ids),
                    "json_path": None,
                    "analysis_path": None,
                    "status": "failed",
                }

            # 4. Подготавливаем информацию о поиске
            search_info = self._build_search_info(data, filters)

            # 5. Подготавливаем автомобили для сохранения в БД
            cars_data = self._prepare_cars_for_db(
                found_cars,
                data["car_type"],
                raw_data_by_id,
            )

            # 6. Формируем JSON с данными рынка
            payload = self._build_market_payload(search_info, found_cars)
            # 7. Сохраняем JSON-файл
            json_path = self._save_market_payload(payload, data)
            # 8. Сохраняем найденные автомобили в PostgreSQL
            self.repository.add_cars(search_id, cars_data)

            # 9. Запускаем GPT-анализ
            analysis = ""
            analysis_error = None
            analysis_path = None
            try:
                analysis = self._analyze_market(payload, language=language)
            except Exception as error:
                logging.exception("Ошибка GPT-анализа")
                analysis_error = str(error)

            # 10. Сохраняем текст GPT-анализа
            if analysis:
                try:
                    analysis_path = self._save_analysis(analysis, json_path)
                except Exception as error:
                    logging.exception("Ошибка сохранения GPT-анализа")
                    analysis_error = f"Не удалось сохранить анализ: {error}"

            # 11. Завершаем поиск в базе данных
            self.repository.complete_search(
                search_id,
                gpt_analysis=analysis,
                gpt_model=DEFAULT_MODEL,
            )
            # 12. Возвращаем результат
            return {
                "search_id": search_id,
                "cars": found_cars,
                "analysis": analysis,
                "analysis_error": analysis_error,
                "total_found": len(car_ids),
                "failed_count": len(failed_ids),
                "json_path": json_path,
                "analysis_path": analysis_path,
                "status": "completed",
            }
        except Exception:
            logging.exception("Ошибка выполнения поиска")
            try:
                self.repository.fail_search(search_id)
            except Exception:
                logging.exception("Не удалось обновить статус поиска")
            raise
