from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SENSOR = ROOT / "custom_components" / "fluidra_local" / "sensor.py"
DEVICE = ROOT / "custom_components" / "fluidra_local" / "device.py"


def test_connection_mode_sensor_is_created_as_diagnostic_entity():
    text = SENSOR.read_text()
    assert "FluidraLocalConnectionSensor" in text
    assert "_attr_name = \"Connection\"" in text
    assert "EntityCategory.DIAGNOSTIC" in text
    assert "native_value" in text


def test_cloud_mode_gets_globe_icon_and_device_configuration_url():
    sensor_text = SENSOR.read_text()
    device_text = DEVICE.read_text()
    assert "mdi:web" in sensor_text
    assert "if self.mode == MODE_CLOUD else None" in sensor_text
    assert "configuration_url" in device_text
    assert "if mode == MODE_CLOUD" in device_text


def test_local_mode_is_default_for_existing_entries():
    text = DEVICE.read_text()
    assert "defaulting old entries to local" in text
    assert "MODE_LOCAL" in text
