"""Sensor platform for Fluidra Local Server integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

SENSORS = [
    ("pool_temperature", "Pool Temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, 10),
    ("air_temperature", "Air Temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, 10),
    ("target_temperature", "Target Temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, 10),
    ("min_setpoint", "Minimum Setpoint", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, 1),
    ("max_setpoint", "Maximum Setpoint", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, 1),
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coord = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([FluidraLocalSensor(coord, *spec) for spec in SENSORS])

class FluidraLocalSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, key: str, name: str, device_class, unit, scale: float) -> None:
        super().__init__(coordinator)
        self.key = key
        self.scale = scale
        self._attr_name = name
        self._attr_unique_id = f"fluidra_local_LG24440781_{key}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get(self.key, {}).get("reportedValue")
        return None if value is None else value / self.scale

    @property
    def device_info(self) -> dict[str, Any]:
        return {"identifiers": {(DOMAIN, "LG24440781")}}
