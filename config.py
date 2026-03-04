import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
MODELS_CACHE_DIR = BASE_DIR / "models_cache"

# ensure dirs exist before we write anything
DATA_DIR.mkdir(exist_ok=True)
MODELS_CACHE_DIR.mkdir(exist_ok=True)