from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FLOW = ROOT / "custom_components" / "fluidra_local" / "config_flow.py"
CONST = ROOT / "custom_components" / "fluidra_local" / "const.py"
MANIFEST = ROOT / "custom_components" / "fluidra_local" / "manifest.json"
INIT = ROOT / "custom_components" / "fluidra_local" / "__init__.py"


def test_config_flow_has_local_and_cloud_connection_mode_steps():
    text = CONFIG_FLOW.read_text()
    assert "CONF_CONNECTION_MODE" in text
    assert "async_step_local" in text
    assert "async_step_cloud" in text
    assert "MODE_LOCAL" in text
    assert "MODE_CLOUD" in text


def test_local_form_mentions_local_server_must_be_running():
    text = (ROOT / "custom_components" / "fluidra_local" / "strings.json").read_text()
    assert "local server must be running" in text.lower()


def test_setup_can_select_cloud_or_local_client():
    text = INIT.read_text()
    assert "MODE_CLOUD" in text
    assert "FluidraCloudClient" in text
    assert "FluidraLocalClient" in text


def test_manifest_uses_fluidra_logo_assets_and_cloud_requirement():
    text = MANIFEST.read_text()
    assert '"logo": "logo.png"' in text
    assert '"icon": "icon.svg"' in text
    assert "boto3" in text


def test_cloud_form_does_not_prompt_for_device_id():
    text = CONFIG_FLOW.read_text()
    cloud_step = text.split("async def async_step_cloud", 1)[1].split("@staticmethod", 1)[0]
    assert "vol.Required(CONF_USERNAME)" in cloud_step
    assert "vol.Required(CONF_PASSWORD)" in cloud_step
    assert "vol.Optional(CONF_DEVICE_ID" not in cloud_step


def test_cloud_flow_stores_device_id_discovered_after_login():
    text = CONFIG_FLOW.read_text()
    cloud_step = text.split("async def async_step_cloud", 1)[1].split("@staticmethod", 1)[0]
    assert "devices = await client.devices()" in cloud_step
    assert "data[CONF_DEVICE_ID] = device_id" in cloud_step


def test_cloud_flow_prompts_for_device_when_login_finds_multiple_devices():
    text = CONFIG_FLOW.read_text()
    assert "async_step_cloud_device" in text
    assert "self._cloud_devices" in text
    assert "len(devices) > 1" in text
    assert "vol.Required(CONF_DEVICE_ID): vol.In" in text


def test_cloud_client_never_falls_back_to_default_device_id_for_discovery():
    text = (ROOT / "custom_components" / "fluidra_local" / "cloud_client.py").read_text()
    ensure_device = text.split("async def _ensure_device_id", 1)[1].split("async def state", 1)[0]
    assert "DEFAULT_DEVICE_ID" not in ensure_device
    assert "raise FluidraCloudClientError" in ensure_device


def test_cloud_client_uses_verified_fluidra_cognito_client_id():
    text = (ROOT / "custom_components" / "fluidra_local" / "cloud_client.py").read_text()
    assert 'COGNITO_CLIENT_ID = "g3njunelkcbtefosqm9bdhhq1"' in text
    assert 'COGNITO_CLIENT_ID = "4s2pr20gcl9fac5okd84q0e1h1"' not in text
