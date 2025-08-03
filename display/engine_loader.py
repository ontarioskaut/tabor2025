import importlib

from config import DISPLAYS


def load_display_engines():
    loaded_displays = []
    for display_cfg in DISPLAYS:
        engine_name = display_cfg["engine"]
        if not engine_name:
            raise ValueError(f"Display {display_cfg['name']} has no engine defined")

        engine_module = importlib.import_module(f"display_engines.{engine_name}")

        engine_class = getattr(engine_module, "Engine", None)
        if not engine_class:
            raise ImportError(f"Engine class not found in {engine_name}")

        engine_instance = engine_class(display_cfg)
        loaded_displays.append({**display_cfg, "engine_instance": engine_instance})

    return loaded_displays
