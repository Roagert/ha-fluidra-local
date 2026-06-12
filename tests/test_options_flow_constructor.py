import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.fluidra_local.config_flow import FluidraLocalOptionsFlow


class ReadOnlyConfigEntryBase:
    @property
    def config_entry(self):
        return object()


def test_options_flow_does_not_assign_readonly_config_entry_property(monkeypatch):
    monkeypatch.setattr(FluidraLocalOptionsFlow, "config_entry", ReadOnlyConfigEntryBase.config_entry, raising=False)
    flow = FluidraLocalOptionsFlow(object())
    assert flow._config_entry is not None
