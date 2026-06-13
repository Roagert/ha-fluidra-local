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


def test_zeroconf_aborts_if_same_local_url_is_already_configured():
    text = CONFIG_FLOW.read_text()
    zeroconf_step = text.split("async def async_step_zeroconf", 1)[1].split("async def async_step_user", 1)[0]
    assert "_abort_if_matching_local_entry_configured(base_url, self._discovered_device_id)" in zeroconf_step
    assert "def _abort_if_matching_local_entry_configured" in text
