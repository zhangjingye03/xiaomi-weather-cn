"""Xiaomi Weather China weather entity."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from homeassistant.components.weather import Forecast, WeatherEntity, WeatherEntityFeature
from homeassistant.const import UnitOfLength, UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from .api import XiaomiWeatherClient
from .const import CONDITIONS, CONF_LATITUDE, CONF_LOCATION_KEY, CONF_LONGITUDE, CONF_STATION_NAME, DOMAIN

SCAN_INTERVAL = timedelta(minutes=10)


def _number(value: Any) -> float | None:
    try:
        return None if value is None or value == "" else float(value)
    except (TypeError, ValueError):
        return None


def _condition(value: Any) -> str:
    return CONDITIONS.get(str(value), "cloudy")


def _items(data: dict[str, Any], key: str) -> list[Any]:
    return data.get(key, {}).get("value", []) or []


def _datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone(timedelta(hours=8)))


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up one configured Xiaomi Weather location."""
    async_add_entities([XiaomiWeatherEntity(hass, entry)], True)


class XiaomiWeatherEntity(WeatherEntity):
    """A polling entity for one Xiaomi Weather location."""

    _attr_has_entity_name = True
    _attr_supported_features = WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_visibility_unit = UnitOfLength.KILOMETERS
    _attr_native_precipitation_unit = UnitOfLength.MILLIMETERS

    def __init__(self, hass, entry) -> None:
        self._entry = entry
        self._client = XiaomiWeatherClient(hass)
        self._data: dict[str, Any] = {}
        self._daily: list[Forecast] = []
        self._hourly: list[Forecast] = []
        self._attr_unique_id = f"xiaomi_weather_{entry.data[CONF_LOCATION_KEY]}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="Xiaomi Weather",
            name=entry.data[CONF_STATION_NAME],
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def attribution(self) -> str:
        return "Xiaomi Weather: Beijing Meteorological Service, Caiyun, CNEMC"

    @property
    def condition(self) -> str:
        return _condition(self._data.get("current", {}).get("weather"))

    @property
    def native_temperature(self): return _number(self._data.get("current", {}).get("temperature", {}).get("value"))
    @property
    def native_apparent_temperature(self): return _number(self._data.get("current", {}).get("feelsLike", {}).get("value"))
    @property
    def humidity(self): return _number(self._data.get("current", {}).get("humidity", {}).get("value"))
    @property
    def native_pressure(self): return _number(self._data.get("current", {}).get("pressure", {}).get("value"))
    @property
    def native_visibility(self): return _number(self._data.get("current", {}).get("visibility", {}).get("value"))
    @property
    def uv_index(self): return _number(self._data.get("current", {}).get("uvIndex"))
    @property
    def wind_bearing(self): return _number(self._data.get("current", {}).get("wind", {}).get("direction", {}).get("value"))
    @property
    def native_wind_speed(self): return _number(self._data.get("current", {}).get("wind", {}).get("speed", {}).get("value"))

    async def async_update(self) -> None:
        self._data = await self._client.async_get_weather(
            self._entry.data[CONF_LATITUDE], self._entry.data[CONF_LONGITUDE], self._entry.data[CONF_LOCATION_KEY]
        )
        self._daily = self._parse_daily(self._data.get("forecastDaily") or {})
        self._hourly = self._parse_hourly(self._data.get("forecastHourly") or {})
        await self.async_update_listeners({"daily", "hourly"})

    async def async_forecast_daily(self) -> list[Forecast] | None: return self._daily or None
    async def async_forecast_hourly(self) -> list[Forecast] | None: return self._hourly or None

    def _parse_daily(self, block: dict[str, Any]) -> list[Forecast]:
        if not (published := block.get("pubTime")): return []
        start = _datetime(published).replace(hour=0, minute=0, second=0, microsecond=0)
        weather, temperatures, probabilities = _items(block, "weather"), _items(block, "temperature"), _items(block, "precipitationProbability")
        speeds, bearings = _items(block.get("wind") or {}, "speed"), _items(block.get("wind") or {}, "direction")
        return [{
            "datetime": _utc(start + timedelta(days=i)), "condition": _condition(item.get("from")),
            "native_temperature": _number((temperatures[i] if i < len(temperatures) else {}).get("from")),
            "native_templow": _number((temperatures[i] if i < len(temperatures) else {}).get("to")),
            "precipitation_probability": _number(probabilities[i]) if i < len(probabilities) else None,
            "native_wind_speed": _number((speeds[i] if i < len(speeds) else {}).get("from")),
            "wind_bearing": _number((bearings[i] if i < len(bearings) else {}).get("from")),
        } for i, item in enumerate(weather)]

    def _parse_hourly(self, block: dict[str, Any]) -> list[Forecast]:
        published = block.get("temperature", {}).get("pubTime")
        if not published: return []
        start, weather, temperatures, wind = _datetime(published).replace(minute=0, second=0, microsecond=0), _items(block, "weather"), _items(block, "temperature"), _items(block, "wind")
        result: list[Forecast] = []
        for i, condition in enumerate(weather):
            item = wind[i] if i < len(wind) else {}
            when = _utc(_datetime(item["datetime"])) if item.get("datetime") else _utc(start + timedelta(hours=i))
            result.append({"datetime": when, "condition": _condition(condition), "native_temperature": _number(temperatures[i]) if i < len(temperatures) else None, "native_wind_speed": _number(item.get("speed")), "wind_bearing": _number(item.get("direction"))})
        return result
