"""Config flow for Fluidra Local Server integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .client import FluidraLocalClient, FluidraLocalClientError
from .const import CONF_AUTH_TOKEN, CONF_BASE_URL, CONF_SCAN_INTERVAL, DEFAULT_AUTH_TOKEN, DEFAULT_BASE_URL, DEFAULT_SCAN_INTERVAL, DOMAIN, MAX_SCAN_INTERVAL, MIN_SCAN_INTERVAL


class FluidraLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fluidra Local Server."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            base_url = user_input[CONF_BASE_URL].rstrip("/")
            auth_token = user_input.get(CONF_AUTH_TOKEN, DEFAULT_AUTH_TOKEN).strip()
            await self.async_set_unique_id(base_url)
            self._abort_if_unique_id_configured()
            client = FluidraLocalClient(base_url, auth_token=auth_token)
            try:
                await client.capabilities()
                await client.component(13)
            except FluidraLocalClientError:
                errors["base"] = "cannot_connect"
            else:
                scan_interval = int(user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
                scan_interval = max(MIN_SCAN_INTERVAL, min(MAX_SCAN_INTERVAL, scan_interval))
                data = {CONF_BASE_URL: base_url}
                if auth_token:
                    data[CONF_AUTH_TOKEN] = auth_token
                return self.async_create_entry(title="Fluidra Local Heat Pump", data=data, options={CONF_SCAN_INTERVAL: scan_interval})

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                vol.Optional(CONF_AUTH_TOKEN, default=DEFAULT_AUTH_TOKEN): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return FluidraLocalOptionsFlow(config_entry)


class FluidraLocalOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Fluidra Local Server."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        base_url = self.config_entry.data[CONF_BASE_URL]

        if user_input is not None:
            auth_token = user_input.get(CONF_AUTH_TOKEN, DEFAULT_AUTH_TOKEN).strip()
            client = FluidraLocalClient(base_url, auth_token=auth_token)
            try:
                await client.capabilities()
                await client.component(13)
            except FluidraLocalClientError:
                errors["base"] = "cannot_connect"
            else:
                scan_interval = int(user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
                scan_interval = max(MIN_SCAN_INTERVAL, min(MAX_SCAN_INTERVAL, scan_interval))
                options = {CONF_SCAN_INTERVAL: scan_interval}
                if auth_token:
                    options[CONF_AUTH_TOKEN] = auth_token
                return self.async_create_entry(title="", data=options)

        schema = vol.Schema({
            vol.Optional(CONF_AUTH_TOKEN, default=self.config_entry.options.get(CONF_AUTH_TOKEN, self.config_entry.data.get(CONF_AUTH_TOKEN, DEFAULT_AUTH_TOKEN))): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
        })
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
