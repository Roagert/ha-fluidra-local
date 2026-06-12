import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from datetime import timedelta

from custom_components.fluidra_local.const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from custom_components.fluidra_local.coordinator import poll_interval_from_options


def test_default_polling_interval_is_30_seconds():
    assert DEFAULT_SCAN_INTERVAL == 30
    assert poll_interval_from_options({}) == timedelta(seconds=30)


def test_polling_interval_can_be_configured():
    assert poll_interval_from_options({CONF_SCAN_INTERVAL: 45}) == timedelta(seconds=45)


def test_polling_interval_is_clamped_to_safe_bounds():
    assert poll_interval_from_options({CONF_SCAN_INTERVAL: 1}) == timedelta(seconds=MIN_SCAN_INTERVAL)
    assert poll_interval_from_options({CONF_SCAN_INTERVAL: 999999}) == timedelta(seconds=MAX_SCAN_INTERVAL)


def test_polling_interval_rejects_bad_values_by_falling_back_to_default():
    assert poll_interval_from_options({CONF_SCAN_INTERVAL: "not-a-number"}) == timedelta(seconds=DEFAULT_SCAN_INTERVAL)
