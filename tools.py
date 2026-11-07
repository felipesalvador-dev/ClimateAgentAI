import json
import os
import urllib.parse
import urllib.request
from datetime import datetime

from strands import tool

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _get_json(url: str, params: dict) -> dict:
    with urllib.request.urlopen(f"{url}?{urllib.parse.urlencode(params)}", timeout=10) as resp:
        return json.load(resp)


@tool
def current_datetime() -> str:
    """Retorna a data e hora atuais do sistema local."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


@tool
def current_temperature(city: str = "") -> dict:
    """Retorna a temperatura atual de uma cidade.

    Args:
        city: Nome da cidade (ex.: "Recife"). Se vazio, usa a cidade padrao configurada.
    """
    city = city.strip() or os.getenv("DEFAULT_CITY", "Sao Paulo")
    try:
        results = _get_json(GEOCODING_URL, {"name": city, "count": 1, "language": "pt"}).get("results")
        if not results:
            return {"erro": f"Cidade '{city}' nao encontrada."}
        place = results[0]
        current = _get_json(
            FORECAST_URL,
            {
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,apparent_temperature,relative_humidity_2m",
                "timezone": "auto",
            },
        )["current"]
    except Exception as e:
        return {"erro": f"Falha ao consultar o clima: {e}"}

    return {
        "cidade": ", ".join(filter(None, [place.get("name"), place.get("admin1"), place.get("country")])),
        "temperatura_c": current["temperature_2m"],
        "sensacao_termica_c": current["apparent_temperature"],
        "umidade_percent": current["relative_humidity_2m"],
        "horario_medicao": current["time"],
    }
