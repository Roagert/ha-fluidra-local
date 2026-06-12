import ast
from pathlib import Path

CONFIG_FLOW = Path(__file__).resolve().parents[1] / "custom_components" / "fluidra_local" / "config_flow.py"


def _tree():
    return ast.parse(CONFIG_FLOW.read_text())


def test_config_flow_options_callback_uses_home_assistant_callback_decorator():
    tree = _tree()
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "FluidraLocalConfigFlow")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "async_get_options_flow")
    decorator_names = {getattr(dec, "id", getattr(dec, "attr", "")) for dec in method.decorator_list}
    assert "staticmethod" in decorator_names
    assert "callback" in decorator_names


def test_config_flow_user_step_exposes_scan_interval_on_new_entries():
    text = CONFIG_FLOW.read_text()
    user_step = text.split("async def async_step_user", 1)[1].split("@staticmethod", 1)[0]
    assert "CONF_SCAN_INTERVAL" in user_step
