from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from stratos.paths import CONFIG_DIR


@lru_cache(maxsize=16)
def load_config(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def config_path(name: str) -> Path:
    return CONFIG_DIR / name
