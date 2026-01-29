import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
MODELS_CACHE_DIR = BASE_DIR / "models_cache"

# Ensure folders exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_CACHE_DIR.mkdir(exist_ok=True)

# THE MICRO-MOMENT DEFINITIONS
# This drives the synthetic data and the Reranker logic
MICRO_MOMENTS = {
    "exam_season": {
        "months": [3, 4], # March/April
        "boost_category": "stationery",
        "personas": ["student_examprep"],
        "active_hours": [21, 22, 23] # Night time
    },
    "diwali_fest": {
        "months": [10, 11], # Oct/Nov
        "boost_category": "home_decor_festive",
        "personas": ["home_decor_festive", "tier2_fashion"],
        "active_hours": [19, 20] # Evening
    },
    "wedding_season": {
        "months": [12, 1, 2],
        "boost_category": "fashion_ethnic",
        "personas": ["tier2_fashion"],
        "active_hours": [14, 15] # Afternoon
    }
}