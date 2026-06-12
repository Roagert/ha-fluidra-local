"""Coordinator for Fluidra Local Server integration."""
from __future__ import annotations

from datetime import timedelta
from typing import Any
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .client import FluidraLocalClient
from .const import DOMAIN

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


class FluidraLocalCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch power/mode/temperature from the local Fluidra server."""

    def __init__(self, hass: HomeAssistant, client: FluidraLocalClient) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=30))
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        data: dict[str, Any] = {"state": await self.client.state(), "capabilities": await self.client.capabilities()}
        for name, cid in READ_COMPONENTS.items():
            try:
                data[name] = await self.client.component(cid)
            except Exception as exc:  # keep entity available with partial data
                _LOGGER.debug("Failed to read Fluidra local component %s/%s: %s", name, cid, exc)
                data[name] = {"id": cid, "error": str(exc)}
        return data
