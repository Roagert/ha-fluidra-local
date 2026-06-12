"""Switch platform for Fluidra Local Server integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
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
    """Set up Fluidra Local power switch."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FluidraLocalPowerSwitch(data["coordinator"], data["client"])])


class FluidraLocalPowerSwitch(CoordinatorEntity, SwitchEntity):
    """Power switch for the heat pump via the local Fluidra bridge."""

    _attr_has_entity_name = True
    _attr_name = "Power"
    _attr_unique_id = "fluidra_local_LG24440781_power_switch"
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_icon = "mdi:power"

    def __init__(self, coordinator, client) -> None:
        super().__init__(coordinator)
        self.client = client

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get("power", {}).get("reportedValue")
        return None if value is None else bool(value)

    @property
    def available(self) -> bool:
        return super().available and self.is_on is not None

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

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.client.power(True, wait=True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.client.power(False, wait=True)
        await self.coordinator.async_request_refresh()
