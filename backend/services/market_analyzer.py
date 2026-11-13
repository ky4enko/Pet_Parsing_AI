import json
import os
from dataclasses import asdict, is_dataclass
from pathlib import Path
from backend.config import SEARCH_DIR
from backend.integrations.openai_client import generate_market_analysis

DEFAULT_MODEL = "gpt-6.1-terra"

SYSTEM_PROMPT = """
Ты — профессиональный аналитик рынка подержанных автомобилей Украины.

Твоя задача — проанализировать объявления AUTO.RIA
и определить ориентировочную рыночную стоимость автомобиля.

Правила анализа:

1. Используй только предоставленные данные.
2. Учитывай марку, модель, год, пробег и модификацию.
3. Не смешивай существенно разные поколения и комплектации.
4. Рассчитай среднюю и медианную цену, если данных достаточно.
5. Найди подозрительно дешёвые и дорогие объявления.
6. Учитывай влияние пробега и года выпуска на стоимость.
7. Определи обоснованный диапазон рыночных цен.
8. Не выдумывай отсутствующие характеристики.
9. Не считай цену объявления подтверждённой ценой продажи.
10. Если данных недостаточно, прямо сообщи об этом.

Формат ответа:

- Отвечай обычным текстом на русском языке.
- Не возвращай JSON.
- Используй понятные заголовки и списки.
- Укажи количество проанализированных объявлений.
- Покажи среднюю и медианную цену.
- Покажи минимальную и максимальную цену.
- Определи разумный диапазон рыночной стоимости.
- Выдели наиболее интересные дешёвые и дорогие объявления.
- Указывай цену, год, пробег и ссылку на объявление, если данные доступны.
- Объясни ограничения анализа.
- В конце дай практический вывод о справедливой цене покупки.
"""


def car_to_dict(car):
    """Преобразует объект автомобиля в словарь."""

    if is_dataclass(car):
        data = asdict(car)
        data.pop("photo_url", None)
        return data

    fields = [
        "car_id",
        "make",
        "model",
        "year",
        "mileage_km",
        "fuel_name",
        "engine_volume_l",
        "gearbox",
        "drive_type",
        "modification_name",
        "price_usd",
        "price_uah",
        "url",
    ]

    return {
        field: getattr(car, field, None)
        for field in fields
    }


def build_market_payload(search_info, cars):
    """Формирует данные объявлений для передачи GPT."""

    return {
        "search_info": search_info,
        "cars": [
            car_to_dict(car)
            for car in cars]
    }


def save_market_payload(
    payload,
    path=SEARCH_DIR / "search_results.json",):
    """Сохраняет исходные объявления в JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            payload,
            file,
            ensure_ascii=False,
            indent=4,
            default=str)
    return output_path


def analyze_market(
    payload,
    model=None,
    max_output_tokens=4000,
    language="ru"):
    """Отправляет объявления GPT и возвращает текстовый анализ."""

    if not payload.get("cars"):
        raise ValueError("Нет автомобилей для анализа.")

    language_names = {
        "ru": "Russian",
        "uk": "Ukrainian",
        "en": "English",
    }

    output_language = language_names.get(language, "Russian")

    instructions = (
        SYSTEM_PROMPT.replace(
            "Отвечай обычным текстом на русском языке.",
            f"Write in {output_language}.")
        + f"\n\nWrite the complete analysis in {output_language}. "
          "All headings, explanations and conclusions must use this language.")

    input_text = (
        f"Analyze the following AUTO.RIA listings. "
        f"Write the complete response in {output_language}; "
        "do not use JSON. "
        "Calculate metrics only from prices actually present "
        "in the supplied data.\n\n"
        + json.dumps(
            payload,
            ensure_ascii=False,
            default=str))

    selected_model = model or os.getenv(
        "OPENAI_MODEL",
        DEFAULT_MODEL)

    return generate_market_analysis(
        model=selected_model,
        instructions=instructions,
        input_text=input_text,
        max_output_tokens=max_output_tokens,)


def save_analysis(
    analysis,
    path=SEARCH_DIR / "ai_analysis.txt",):
    """Сохраняет текстовый анализ в TXT."""
    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(str(analysis))
    return output_path