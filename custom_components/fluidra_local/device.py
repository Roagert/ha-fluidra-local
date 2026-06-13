"""Shared device metadata helpers for Fluidra Local integration."""
from __future__ import annotations

from typing import Any

from .const import DOMAIN, MODE_CLOUD, MODE_LOCAL

CLOUD_CONFIGURATION_URL = "https://www.fluidra.com/"
DEFAULT_DEVICE_NAME = "Fluidra Local Heat Pump"
DEFAULT_DEVICE_MODEL = "Swim & Fun Inverter Heat Pump"
DEFAULT_DEVICE_ID = "LG24440781"


def integration_mode(entry_data: dict[str, Any] | None) -> str:
    """Return the configured connection mode, defaulting old entries to local."""
    mode = (entry_data or {}).get("connection_mode", MODE_LOCAL)
    return MODE_CLOUD if mode == MODE_CLOUD else MODE_LOCAL


def device_id_from_coordinator(coordinator: Any) -> str:
    """Return the device id advertised by the bridge/cloud snapshot."""
    data = getattr(coordinator, "data", None) or {}
    return (
        data.get("state", {}).get("device", {}).get("id")
        or data.get("state", {}).get("device_id")
        or data.get("capabilities", {}).get("device_id")
        or DEFAULT_DEVICE_ID
    )


def fluidra_device_info(coordinator: Any, mode: str = MODE_LOCAL) -> dict[str, Any]:
    """Return the HA device-info block used by every Fluidra entity.

    Cloud mode includes a configuration URL so the HA device page shows the
    external/globe affordance. Local mode intentionally omits it.
    """
    info: dict[str, Any] = {
        "identifiers": {(DOMAIN, device_id_from_coordinator(coordinator))},
        "name": DEFAULT_DEVICE_NAME,
        "manufacturer": "Fluidra",
        "model": DEFAULT_DEVICE_MODEL,
    }
    if mode == MODE_CLOUD:
        info["configuration_url"] = CLOUD_CONFIGURATION_URL
    return info
