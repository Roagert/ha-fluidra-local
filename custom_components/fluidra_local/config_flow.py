"""Config flow for Fluidra Local Server integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .client import FluidraLocalClient, FluidraLocalClientError
from .const import CONF_BASE_URL, DEFAULT_BASE_URL, DOMAIN


class FluidraLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fluidra Local Server."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            base_url = user_input[CONF_BASE_URL].rstrip("/")
            await self.async_set_unique_id(base_url)
            self._abort_if_unique_id_configured()
            client = FluidraLocalClient(base_url)
            try:
                await client.capabilities()
                await client.component(13)
            except FluidraLocalClientError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="Fluidra Local Heat Pump", data={CONF_BASE_URL: base_url})

        schema = vol.Schema({vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
