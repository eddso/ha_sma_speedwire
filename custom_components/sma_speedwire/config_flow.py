"""Config flow for sma_speedwire integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from .sma_speedwire import SMA_SPEEDWIRE, smaError

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str, 
    vol.Required(CONF_PASSWORD): str,
})

class SMASpeedWireConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for sma_speedwire."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                api = SMA_SPEEDWIRE(user_input[CONF_HOST], user_input[CONF_PASSWORD],_LOGGER)
                await self.hass.async_add_executor_job(api.init)
            except (smaError):
                _LOGGER.exception("Cannot connect to inverter")
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=api.inv_class,
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
