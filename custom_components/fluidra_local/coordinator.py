"""Coordinator for Fluidra Local Server integration."""
from __future__ import annotations

from datetime import timedelta
from typing import Any
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .client import FluidraLocalClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, MAX_SCAN_INTERVAL, MIN_SCAN_INTERVAL, CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

READ_COMPONENTS = {
    "power": 13,
    "mode": 14,
    "target_temperature": 15,
    "pool_temperature": 19,
    "flow_status": 28,
    "air_temperature": 67,
    "min_setpoint": 81,
    "max_setpoint": 82,
}


def poll_interval_from_options(options: dict[str, Any] | None) -> timedelta:
    """Return a safe polling interval for Fluidra state refreshes."""
    raw_value = (options or {}).get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    try:
        seconds = int(raw_value)
    except (TypeError, ValueError):
        seconds = DEFAULT_SCAN_INTERVAL
    seconds = max(MIN_SCAN_INTERVAL, min(MAX_SCAN_INTERVAL, seconds))
    return timedelta(seconds=seconds)


def map_components_by_id(components: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Return a component-id keyed map from a bulk bridge component snapshot."""
    mapped: dict[int, dict[str, Any]] = {}
    for component in components:
        try:
            mapped[int(component["id"])] = component
        except (KeyError, TypeError, ValueError):
            continue
    return mapped


def read_components_from_bulk(components: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Return the named HA component payloads from one bridge /components read."""
    by_id = map_components_by_id(components)
    return {
        name: by_id.get(cid, {"id": cid, "error": "missing from bulk component snapshot"})
        for name, cid in READ_COMPONENTS.items()
    }


class FluidraLocalCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch power/mode/temperature from the local Fluidra server."""

    def __init__(self, hass: HomeAssistant, client: FluidraLocalClient, options: dict[str, Any] | None = None) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=poll_interval_from_options(options))
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        data: dict[str, Any] = {"state": await self.client.state(), "capabilities": await self.client.capabilities()}
        try:
            data.update(read_components_from_bulk(await self.client.components()))
        except Exception as exc:  # keep entity available with partial data if bulk read fails
            _LOGGER.debug("Failed to read Fluidra local bulk components: %s", exc)
            for name, cid in READ_COMPONENTS.items():
                try:
                    data[name] = await self.client.component(cid)
                except Exception as component_exc:
                    _LOGGER.debug("Failed to read Fluidra local component %s/%s: %s", name, cid, component_exc)
                    data[name] = {"id": cid, "error": str(component_exc)}
        return data
