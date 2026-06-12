"""Climate entity for Fluidra Local Server integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature
from homeassistant.components.climate.const import HVACAction, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, VALUE_TO_MODE, MODE_TO_VALUE

PRESET_TO_HVAC = {
    "Smart Auto": HVACMode.AUTO,
    "Smart Heating": HVACMode.HEAT,
    "Boost Heating": HVACMode.HEAT,
    "Silence Heating": HVACMode.HEAT,
    "Smart Cooling": HVACMode.COOL,
    "Boost Cooling": HVACMode.COOL,
    "Silence Cooling": HVACMode.COOL,
}
HVAC_TO_PRESET = {
    HVACMode.AUTO: "Smart Auto",
    HVACMode.HEAT: "Smart Heating",
    HVACMode.COOL: "Smart Cooling",
}


def _scaled(component: dict[str, Any] | None, scale: float = 10.0) -> float | None:
    if not isinstance(component, dict):
        return None
    value = component.get("reportedValue")
    return None if value is None else value / scale


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FluidraLocalClimate(data["coordinator"], data["client"])])


class FluidraLocalClimate(CoordinatorEntity, ClimateEntity):
    """Heat pump controlled through the local Fluidra server."""

    _attr_has_entity_name = True
    _attr_name = "Pool Heat Pump"
    _attr_unique_id = "fluidra_local_LG24440781_climate"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.1
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.HEAT, HVACMode.COOL]
    _attr_preset_modes = list(MODE_TO_VALUE.keys())

    def __init__(self, coordinator, client) -> None:
        super().__init__(coordinator)
        self.client = client

    @property
    def min_temp(self) -> float:
        return _scaled(self.coordinator.data.get("min_setpoint"), 1.0) or 8.1

    @property
    def max_temp(self) -> float:
        return _scaled(self.coordinator.data.get("max_setpoint"), 1.0) or 40.0

    @property
    def device_info(self) -> dict[str, Any]:
        device_id = self.coordinator.data.get("state", {}).get("device", {}).get("id") or self.coordinator.data.get("capabilities", {}).get("device_id", "LG24440781")
        return {"identifiers": {(DOMAIN, device_id)}, "name": "Fluidra Local Heat Pump", "manufacturer": "Fluidra", "model": "Swim & Fun Inverter Heat Pump"}

    @property
    def hvac_mode(self) -> HVACMode:
        if self.coordinator.data.get("power", {}).get("reportedValue") == 0:
            return HVACMode.OFF
        return PRESET_TO_HVAC.get(self.preset_mode, HVACMode.HEAT)

    @property
    def hvac_action(self) -> HVACAction:
        return HVACAction.OFF if self.hvac_mode == HVACMode.OFF else HVACAction.HEATING

    @property
    def preset_mode(self) -> str | None:
        return VALUE_TO_MODE.get(self.coordinator.data.get("mode", {}).get("reportedValue"))

    @property
    def target_temperature(self) -> float | None:
        return _scaled(self.coordinator.data.get("target_temperature"), 10.0)

    @property
    def current_temperature(self) -> float | None:
        return _scaled(self.coordinator.data.get("pool_temperature"), 10.0)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.client.power(False, wait=True)
        else:
            await self.client.power(True, wait=True)
            preset = HVAC_TO_PRESET.get(hvac_mode)
            if preset:
                await self.client.set_mode(preset, wait=True)
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        await self.client.set_mode(preset_mode, wait=True)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return
        await self.client.set_temperature(float(kwargs[ATTR_TEMPERATURE]), wait=True)
        await self.coordinator.async_request_refresh()
