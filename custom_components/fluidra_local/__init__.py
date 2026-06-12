"""Fluidra Local Server Home Assistant integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .client import FluidraLocalClient
from .const import CONF_AUTH_TOKEN, CONF_BASE_URL, DOMAIN, PLATFORMS
from .coordinator import FluidraLocalCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fluidra Local Server from a config entry."""
    auth_token = entry.options.get(CONF_AUTH_TOKEN) or entry.data.get(CONF_AUTH_TOKEN)
    client = FluidraLocalClient(entry.data[CONF_BASE_URL], auth_token=auth_token)
    coordinator = FluidraLocalCoordinator(hass, client, {**entry.data, **entry.options})
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"client": client, "coordinator": coordinator}
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when integration options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
