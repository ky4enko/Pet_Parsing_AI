import os
import requests
from dotenv import load_dotenv
import logging
import json

logging.basicConfig(filename="app.log", level=logging.ERROR,
                    format="%(asctime)s | %(levelname)s | %(message)s", encoding="utf-8")

load_dotenv()
API_KEY = os.getenv("AUTO_RIA_API")
if not API_KEY:
    raise ValueError("API key not found in .env file")
# Wrapper error log
def api_get_json(url, params):
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as error:
        status_code =(error.response.status_code if error.response is not None else "Unknown")
        logging.error("HTTP-error. Code: %s", status_code)
        raise
    except requests.RequestException as error:
        logging.error("Request error. Type: %s", type(error).__name__)
        raise
    except ValueError:
        logging.error("JSON parsing error")
        raise