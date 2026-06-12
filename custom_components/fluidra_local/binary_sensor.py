"""Binary sensors for Fluidra Local Server integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coord = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([FluidraLocalFlowSensor(coord)])

class FluidraLocalFlowSensor(CoordinatorEntity, BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "No Flow"
    _attr_unique_id = "fluidra_local_LG24440781_no_flow"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get("flow_status", {}).get("reportedValue")
        return None if value is None else bool(value)

    @property
    def device_info(self) -> dict[str, Any]:
        return {"identifiers": {(DOMAIN, "LG24440781")}}
