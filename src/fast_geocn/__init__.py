"""Fast-GeoCN: 超轻量离线中国行政区划逆地理编码（仅依赖 shapely）。"""

from .core import reverse_geocode, regeo
from .coord import (
    wgs84_to_gcj02,
    gcj02_to_wgs84,
    gcj02_to_bd09,
    bd09_to_gcj02,
    wgs84_to_bd09,
    bd09_to_wgs84,
)

__version__ = "1.1.0"
__all__ = [
    "reverse_geocode",
    "regeo",
    "wgs84_to_gcj02",
    "gcj02_to_wgs84",
    "gcj02_to_bd09",
    "bd09_to_gcj02",
    "wgs84_to_bd09",
    "bd09_to_wgs84",
]
