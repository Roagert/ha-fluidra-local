from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FLOW = ROOT / "custom_components" / "fluidra_local" / "config_flow.py"
MANIFEST = ROOT / "custom_components" / "fluidra_local" / "manifest.json"
STRINGS = ROOT / "custom_components" / "fluidra_local" / "strings.json"


def test_manifest_declares_fluidra_local_zeroconf_service():
    text = MANIFEST.read_text()
    assert '"zeroconf"' in text
    assert '"_fluidra-local._tcp.local."' in text


def test_config_flow_accepts_zeroconf_discovery_and_prefills_local_url():
    text = CONFIG_FLOW.read_text()
    assert "async_step_zeroconf" in text
    assert "discovery_info: Any" in text
    assert "_discovered_base_url" in text
    assert 'f"http://{discovery_info.host}:{discovery_info.port}"' in text
    assert 'vol.Required(CONF_BASE_URL, default=self._discovered_base_url or DEFAULT_BASE_URL)' in text


def test_local_form_mentions_mdns_autofill():
    text = STRINGS.read_text()
    assert "_fluidra-local._tcp.local" in text
    assert "auto-fills the URL" in text
