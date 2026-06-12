import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.fluidra_local.state_values import component_value


def test_command_state_prefers_desired_value_when_external_app_changes_setpoint():
    component = {"id": 15, "desiredValue": 290, "reportedValue": 300}
    assert component_value(component, prefer_desired=True) == 290


def test_command_state_falls_back_to_reported_value_when_desired_missing():
    component = {"id": 15, "reportedValue": 300}
    assert component_value(component, prefer_desired=True) == 300


def test_actual_temperature_uses_reported_value_not_desired_value():
    component = {"id": 19, "desiredValue": 999, "reportedValue": 123}
    assert component_value(component, prefer_desired=False) == 123
