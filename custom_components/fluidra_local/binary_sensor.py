"""Binary sensors for Fluidra Local Server integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fluidra Local binary sensors."""
    coord = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([FluidraLocalNoFlowErrorSensor(coord)])


class FluidraLocalNoFlowErrorSensor(CoordinatorEntity, BinarySensorEntity):
    """Problem entity that turns on when the heat pump reports a no-flow error."""

    _attr_has_entity_name = True
    _attr_name = "No Flow Error"
    _attr_unique_id = "fluidra_local_LG24440781_no_flow"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:pipe-disconnected"

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get("flow_status", {}).get("reportedValue")
        # Component 28: 0 means normal/OK; any non-zero value is a no-flow problem.
        return None if value is None else bool(value)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        component = self.coordinator.data.get("flow_status", {})
        value = component.get("reportedValue")
        return {
            "component_id": component.get("id", 28),
            "reported_value": value,
            "meaning": "OK / flow present" if value == 0 else "No-flow error reported by heat pump",
            "normal_value": 0,
            "problem_when_nonzero": True,
        }

    @property
    def device_info(self) -> dict[str, Any]:
        device_id = (
            self.coordinator.data.get("state", {}).get("device", {}).get("id")
            or self.coordinator.data.get("capabilities", {}).get("device_id", "LG24440781")
        )
        return {
            "identifiers": {(DOMAIN, device_id)},
            "name": "Fluidra Local Heat Pump",
            "manufacturer": "Fluidra",
            "model": "Swim & Fun Inverter Heat Pump",
        }
