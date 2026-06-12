"""Helpers for selecting Fluidra component state values."""
from __future__ import annotations

from typing import Any


def component_value(component: dict[str, Any] | None, *, prefer_desired: bool = False) -> Any | None:
    """Return the best state value from a Fluidra component payload.

    Fluidra command/state components can show changes made by the official app
    as desiredValue before reportedValue converges. For command-like HA entity
    state (power/mode/setpoint), prefer desiredValue when present so external app
    changes appear on the next poll. Physical readings must keep using
    reportedValue.
    """
    if not isinstance(component, dict):
        return None
    if prefer_desired and component.get("desiredValue") is not None:
        return component.get("desiredValue")
    return component.get("reportedValue")
