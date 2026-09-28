import requests

from langchain.tools import tool


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


@tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a city using the real Open-Meteo REST API.
    Use this when the user asks for current weather or weather conditions.
    """

    try:
        # ----------------------------------------
        # 1. Convert city name -> latitude/longitude
        # ----------------------------------------
        geo_response = requests.get(
            GEOCODING_URL,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=10,
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        results = geo_data.get("results")

        if not results:
            return f"Could not find the location: {city}"

        location = results[0]

        latitude = location["latitude"]
        longitude = location["longitude"]
        resolved_name = location["name"]
        country = location.get("country", "")

        # ----------------------------------------
        # 2. Call real weather API
        # ----------------------------------------
        weather_response = requests.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "wind_speed_10m"
                ),
                "timezone": "auto",
            },
            timeout=10,
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        current = weather_data.get("current", {})
        units = weather_data.get("current_units", {})

        return (
            f"Weather for {resolved_name}, {country}\n"
            f"Temperature: {current.get('temperature_2m')} "
            f"{units.get('temperature_2m', '°C')}\n"
            f"Feels like: {current.get('apparent_temperature')} "
            f"{units.get('apparent_temperature', '°C')}\n"
            f"Humidity: {current.get('relative_humidity_2m')} "
            f"{units.get('relative_humidity_2m', '%')}\n"
            f"Wind speed: {current.get('wind_speed_10m')} "
            f"{units.get('wind_speed_10m', 'km/h')}\n"
            f"Observation time: {current.get('time')}"
        )

    except requests.RequestException as exc:
        return f"Weather API request failed: {exc}"

    except Exception as exc:
        return f"Weather tool failed: {exc}"