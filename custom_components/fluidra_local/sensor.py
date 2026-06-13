"""Sensor platform for Fluidra Local Server integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import MODE_CLOUD
from .device import fluidra_device_info, integration_mode
from .const import DOMAIN
from .state_values import component_value

SENSORS = [
    ("pool_temperature", "Pool Temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, 10),
    ("air_temperature", "Air Temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, 10),
    ("target_temperature", "Target Temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, 10),
    ("min_setpoint", "Minimum Setpoint", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, 1),
    ("max_setpoint", "Maximum Setpoint", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, 1),
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coord = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    mode = integration_mode(entry.data)
    async_add_entities(
        [FluidraLocalConnectionSensor(coord, mode)]
        + [FluidraLocalSensor(coord, mode, *spec) for spec in SENSORS]
    )

class FluidraLocalConnectionSensor(CoordinatorEntity, SensorEntity):
    """Diagnostic sensor showing whether this entry uses local bridge or cloud."""

    _attr_has_entity_name = True
    _attr_name = "Connection"
    _attr_unique_id = "fluidra_local_LG24440781_connection"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, mode: str) -> None:
        super().__init__(coordinator)
        self.mode = mode

    @property
    def native_value(self) -> str:
        return self.mode

    @property
    def icon(self) -> str | None:
        return "mdi:web" if self.mode == MODE_CLOUD else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "local_server_required": self.mode != MODE_CLOUD,
        }

    @property
    def device_info(self) -> dict[str, Any]:
        return fluidra_device_info(self.coordinator, self.mode)

class FluidraLocalSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, mode: str, key: str, name: str, device_class, unit, scale: float) -> None:
        super().__init__(coordinator)
        self.key = key
        self.mode = mode
        self.scale = scale
        self._attr_name = name
        self._attr_unique_id = f"fluidra_local_LG24440781_{key}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self) -> float | None:
        value = component_value(self.coordinator.data.get(self.key), prefer_desired=self.key in {"target_temperature"})
        return None if value is None else value / self.scale

    @property
    def device_info(self) -> dict[str, Any]:
        return fluidra_device_info(self.coordinator, self.mode)
