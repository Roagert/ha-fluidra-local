from pathlib import Path

SWITCH = Path(__file__).resolve().parents[1] / "custom_components" / "fluidra_local" / "switch.py"


def test_power_switch_sets_optimistic_coordinator_state_after_command_acceptance():
    text = SWITCH.read_text()
    assert "def _set_optimistic_power_state" in text
    assert "desiredValue" in text
    assert "async_set_updated_data" in text
    assert "_set_optimistic_power_state(True)" in text
    assert "_set_optimistic_power_state(False)" in text
