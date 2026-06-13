from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "fluidra_local"

# SHA256 values from Roagert/ha-fluidra-pool custom_components/fluidra_pool assets.
OLD_FLUIDRA_POOL_ICON_SHA256 = "cb5157af1eeb601be18f867b13ae547fe462584727f69e51672a69eb322bda4c"
OLD_FLUIDRA_POOL_LOGO_SHA256 = "d4a3f303ea05985040b13ab0ef701651045d8bece5fa90eafe818e2b326d2b9b"


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def test_integration_uses_original_fluidra_pool_icon_asset():
    assert _sha(INTEGRATION / "icon.svg") == OLD_FLUIDRA_POOL_ICON_SHA256


def test_integration_uses_original_fluidra_pool_logo_asset():
    assert _sha(INTEGRATION / "logo.png") == OLD_FLUIDRA_POOL_LOGO_SHA256
