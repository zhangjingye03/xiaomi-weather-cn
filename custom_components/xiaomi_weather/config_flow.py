"""Config flow for Xiaomi Weather China."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .api import XiaomiWeatherClient, XiaomiWeatherError
from .const import CONF_LOCATION_KEY, CONF_STATION_NAME, DOMAIN


class XiaomiWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure one Xiaomi Weather location."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Accept a display name plus location coordinates."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                client = XiaomiWeatherClient(self.hass)
                resolved = await client.async_resolve_location(
                    user_input[CONF_LATITUDE], user_input[CONF_LONGITUDE]
                )
                location_key = str(resolved["locationKey"]).removeprefix("weathercn:")
                title = user_input[CONF_NAME].strip() or resolved.get("name") or location_key
                await self.async_set_unique_id(f"{DOMAIN}_{location_key}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_STATION_NAME: title,
                        CONF_LOCATION_KEY: location_key,
                        CONF_LATITUDE: user_input[CONF_LATITUDE],
                        CONF_LONGITUDE: user_input[CONF_LONGITUDE],
                    },
                )
            except XiaomiWeatherError:
                errors["base"] = "cannot_connect"
            except (KeyError, TypeError, ValueError):
                errors["base"] = "invalid_location"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_LATITUDE): vol.Coerce(float),
                    vol.Required(CONF_LONGITUDE): vol.Coerce(float),
                }
            ),
            errors=errors,
        )
