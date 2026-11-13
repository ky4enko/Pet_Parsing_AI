from openai import OpenAI
from backend.config import get_openai_api_key

def generate_market_analysis(
    model: str,
    instructions: str,
    input_text: str,
    max_output_tokens: int = 4000,
) -> str:
    """Отправляет запрос OpenAI и возвращает текст ответа."""

    client = OpenAI(api_key=get_openai_api_key())

    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=input_text,
        store=False)

    if response.status != "completed":
        details = getattr(
            response,
            "incomplete_details",
            None)

        raise RuntimeError(
            "GPT не завершил формирование ответа. "
            f"Статус: {response.status}. "
            f"Подробности: {details}")

    analysis_text = response.output_text

    if not analysis_text or not analysis_text.strip():
        raise RuntimeError("GPT вернул пустой ответ.")
    return analysis_text.strip()