from pathlib import Path

from custom_components.fluidra_local.coordinator import READ_COMPONENTS, map_components_by_id, read_components_from_bulk


def test_read_components_from_bulk_maps_single_bridge_snapshot_to_named_components():
    bulk = [
        {"id": 13, "reportedValue": 1},
        {"id": 19, "reportedValue": 181},
        {"id": 999, "reportedValue": "ignored"},
    ]

    mapped = read_components_from_bulk(bulk)

    assert mapped["power"] == {"id": 13, "reportedValue": 1}
    assert mapped["pool_temperature"] == {"id": 19, "reportedValue": 181}
    assert mapped["mode"] == {"id": 14, "error": "missing from bulk component snapshot"}


def test_coordinator_uses_bulk_components_endpoint_not_one_http_call_per_component():
    text = (Path(__file__).resolve().parents[1] / "custom_components" / "fluidra_local" / "coordinator.py").read_text()
    assert "await self.client.components()" in text
    assert "for name, cid in READ_COMPONENTS.items():\n            try:\n                data[name] = await self.client.component(cid)" not in text


def test_client_exposes_bulk_components_endpoint():
    text = (Path(__file__).resolve().parents[1] / "custom_components" / "fluidra_local" / "client.py").read_text()
    assert "async def components" in text
    assert 'self.request("GET", "/components")' in text
