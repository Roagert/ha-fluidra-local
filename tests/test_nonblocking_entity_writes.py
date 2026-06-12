from pathlib import Path


def test_entity_service_handlers_do_not_block_waiting_for_fluidra_convergence():
    integration_dir = Path(__file__).resolve().parents[1] / "custom_components" / "fluidra_local"
    offenders = []
    for path in (integration_dir / "climate.py", integration_dir / "switch.py"):
        for line_number, line in enumerate(path.read_text().splitlines(), 1):
            if "wait=True" in line:
                offenders.append(f"{path.name}:{line_number}:{line.strip()}")
    assert offenders == []
