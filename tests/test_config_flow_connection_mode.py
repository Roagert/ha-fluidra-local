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
