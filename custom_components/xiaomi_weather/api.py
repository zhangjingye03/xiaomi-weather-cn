"""Xiaomi Weather China API client."""

from __future__ import annotations

from typing import Any

import aiohttp

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import APP_KEY, BASE_URL, FORECAST_PATH, GEO_PATH, SIGN


class XiaomiWeatherError(HomeAssistantError):
    """The Xiaomi Weather endpoint did not yield usable data."""


class XiaomiWeatherClient:
    """Small async client for Xiaomi Weather's China endpoint."""

    def __init__(self, hass) -> None:
        self._session = async_get_clientsession(hass)

    async def _get(self, path: str, params: dict[str, Any]) -> Any:
        try:
            async with self._session.get(
                f"{BASE_URL}{path}", params=params, timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                response.raise_for_status()
                return await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise XiaomiWeatherError(f"Xiaomi Weather request failed: {err}") from err

    async def async_resolve_location(self, latitude: float, longitude: float) -> dict[str, Any]:
        """Resolve coordinates into Xiaomi's weathercn location key."""
        result = await self._get(
            GEO_PATH,
            {"latitude": latitude, "longitude": longitude, "locale": "zh_CN"},
        )
        if not isinstance(result, dict) or not result.get("locationKey"):
            raise XiaomiWeatherError("Xiaomi Weather could not resolve this location")
        return result

    async def async_get_weather(
        self, latitude: float, longitude: float, location_key: str
    ) -> dict[str, Any]:
        """Return current weather plus hourly and daily forecasts."""
        key = location_key.removeprefix("weathercn:")
        result = await self._get(
            FORECAST_PATH,
            {
                "latitude": latitude,
                "longitude": longitude,
                "isLocated": "false",
                "locationKey": f"weathercn:{key}",
                "days": 15,
                "appKey": APP_KEY,
                "sign": SIGN,
                "isGlobal": "false",
                "locale": "zh_cn",
            },
        )
        if not isinstance(result, dict) or not result.get("current"):
            raise XiaomiWeatherError("Xiaomi Weather returned no current observation")
        return result
