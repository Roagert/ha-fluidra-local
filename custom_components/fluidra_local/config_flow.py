"""Config flow for Fluidra Local Server integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.zeroconf import ZeroconfServiceInfo
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .client import FluidraLocalClient, FluidraLocalClientError
from .cloud_client import FluidraCloudClient, FluidraCloudClientError
from .const import (
    CONF_AUTH_TOKEN,
    CONF_BASE_URL,
    CONF_CONNECTION_MODE,
    CONF_DEVICE_ID,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    CONNECTION_MODES,
    DEFAULT_AUTH_TOKEN,
    DEFAULT_BASE_URL,
    DEFAULT_DEVICE_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    MODE_CLOUD,
    MODE_LOCAL,
)


class FluidraLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fluidra Local Server."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered_base_url: str | None = None
        self._discovered_device_id: str | None = None
        self._discovered_auth_required = False

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> FlowResult:
        """Handle mDNS discovery from the local Fluidra bridge."""
        properties = discovery_info.properties or {}
        base_url = str(properties.get(CONF_BASE_URL) or properties.get("base_url") or f"http://{discovery_info.host}:{discovery_info.port}").rstrip("/")
        self._discovered_base_url = base_url
        self._discovered_device_id = str(properties.get(CONF_DEVICE_ID) or properties.get("device_id") or DEFAULT_DEVICE_ID)
        self._discovered_auth_required = str(properties.get("auth_required", "0")).lower() in {"1", "true", "yes"}
        await self.async_set_unique_id(f"{MODE_LOCAL}:{base_url}")
        self._abort_if_unique_id_configured()
        self.context["title_placeholders"] = {"name": "Fluidra Local Bridge"}
        return await self.async_step_local()

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Choose local bridge or direct cloud mode."""
        if user_input is not None:
            mode = user_input[CONF_CONNECTION_MODE]
            if mode == MODE_CLOUD:
                return await self.async_step_cloud()
            return await self.async_step_local()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_CONNECTION_MODE, default=MODE_LOCAL): vol.In(CONNECTION_MODES)}),
            errors={},
        )

    async def async_step_local(self, user_input: dict | None = None) -> FlowResult:
        """Configure local bridge mode. The local server must be running."""
        errors: dict[str, str] = {}
        if user_input is not None:
            base_url = user_input[CONF_BASE_URL].rstrip("/")
            device_id = user_input.get(CONF_DEVICE_ID, self._discovered_device_id or DEFAULT_DEVICE_ID)
            auth_token = user_input.get(CONF_AUTH_TOKEN, DEFAULT_AUTH_TOKEN).strip()
            await self.async_set_unique_id(f"{MODE_LOCAL}:{base_url}")
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
                data = {CONF_CONNECTION_MODE: MODE_LOCAL, CONF_BASE_URL: base_url}
                if device_id:
                    data[CONF_DEVICE_ID] = device_id
                if auth_token:
                    data[CONF_AUTH_TOKEN] = auth_token
                return self.async_create_entry(title="Fluidra Local Heat Pump", data=data, options={CONF_SCAN_INTERVAL: scan_interval})

        return self.async_show_form(
            step_id="local",
            data_schema=vol.Schema({
                vol.Required(CONF_BASE_URL, default=self._discovered_base_url or DEFAULT_BASE_URL): str,
                vol.Optional(CONF_DEVICE_ID, default=self._discovered_device_id or DEFAULT_DEVICE_ID): str,
                vol.Optional(CONF_AUTH_TOKEN, default=DEFAULT_AUTH_TOKEN): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
            }),
            errors=errors,
        )

    async def async_step_cloud(self, user_input: dict | None = None) -> FlowResult:
        """Configure direct Fluidra cloud mode."""
        errors: dict[str, str] = {}
        if user_input is not None:
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_PASSWORD]
            device_id = user_input.get(CONF_DEVICE_ID, "").strip()
            await self.async_set_unique_id(f"{MODE_CLOUD}:{username}:{device_id or DEFAULT_DEVICE_ID}")
            self._abort_if_unique_id_configured()
            client = FluidraCloudClient(username, password, device_id=device_id or None)
            try:
                await client.components()
            except FluidraCloudClientError as exc:
                errors["base"] = "invalid_auth" if "invalid_auth" in str(exc) else "cannot_connect"
            else:
                scan_interval = int(user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
                scan_interval = max(MIN_SCAN_INTERVAL, min(MAX_SCAN_INTERVAL, scan_interval))
                data = {CONF_CONNECTION_MODE: MODE_CLOUD, CONF_USERNAME: username, CONF_PASSWORD: password}
                if device_id:
                    data[CONF_DEVICE_ID] = device_id
                return self.async_create_entry(title="Fluidra Cloud Heat Pump", data=data, options={CONF_SCAN_INTERVAL: scan_interval})

        return self.async_show_form(
            step_id="cloud",
            data_schema=vol.Schema({
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_DEVICE_ID, default=""): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return FluidraLocalOptionsFlow(config_entry)


class FluidraLocalOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Fluidra Local Server."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        mode = self._config_entry.data.get(CONF_CONNECTION_MODE, MODE_LOCAL)
        if user_input is not None:
            scan_interval = int(user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
            scan_interval = max(MIN_SCAN_INTERVAL, min(MAX_SCAN_INTERVAL, scan_interval))
            options = {CONF_SCAN_INTERVAL: scan_interval}
            if mode == MODE_LOCAL:
                auth_token = user_input.get(CONF_AUTH_TOKEN, DEFAULT_AUTH_TOKEN).strip()
                client = FluidraLocalClient(self._config_entry.data[CONF_BASE_URL], auth_token=auth_token)
                try:
                    await client.capabilities()
                    await client.component(13)
                except FluidraLocalClientError:
                    errors["base"] = "cannot_connect"
                else:
                    if auth_token:
                        options[CONF_AUTH_TOKEN] = auth_token
                    return self.async_create_entry(title="", data=options)
            else:
                return self.async_create_entry(title="", data=options)

        schema_data = {vol.Optional(CONF_SCAN_INTERVAL, default=self._config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL))}
        if mode == MODE_LOCAL:
            schema_data[vol.Optional(CONF_AUTH_TOKEN, default=self._config_entry.options.get(CONF_AUTH_TOKEN, self._config_entry.data.get(CONF_AUTH_TOKEN, DEFAULT_AUTH_TOKEN)))] = str
        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema_data), errors=errors)
