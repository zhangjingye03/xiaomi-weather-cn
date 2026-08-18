"""Constants for Xiaomi Weather China."""

from homeassistant.const import Platform

DOMAIN = "xiaomi_weather"
PLATFORMS: list[Platform] = [Platform.WEATHER]

CONF_LOCATION_KEY = "location_key"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_STATION_NAME = "station_name"

BASE_URL = "https://weatherapi.market.xiaomi.com/wtr-v3/"
FORECAST_PATH = "weather/all"
GEO_PATH = "location/city/geo"

# These values are used by Xiaomi Weather's public mobile-client endpoint.
# They are not user credentials and must never be confused with a private API key.
APP_KEY = "weather20151024"
SIGN = "zUFJoAR2ZVrDy1vF3D07"

CONDITIONS = {
    "0": "sunny", "1": "partlycloudy", "2": "cloudy", "3": "rainy",
    "4": "lightning-rainy", "5": "hail", "6": "snowy-rainy",
    "7": "rainy", "8": "rainy", "9": "pouring", "10": "pouring",
    "11": "pouring", "12": "pouring", "13": "snowy", "14": "snowy",
    "15": "snowy", "16": "snowy", "17": "snowy", "18": "fog",
    "19": "snowy-rainy", "20": "windy", "21": "rainy", "22": "rainy",
    "23": "pouring", "24": "pouring", "25": "pouring", "26": "snowy",
    "27": "snowy", "28": "snowy", "29": "windy", "30": "windy",
    "31": "windy", "32": "fog", "49": "fog", "53": "fog",
    "54": "fog", "55": "fog", "56": "fog", "57": "fog",
}
