"""Fast-GeoCN: 超轻量离线中国行政区划逆地理编码（仅依赖 shapely）。"""

from .core import reverse_geocode, regeo

__version__ = "1.0.0"
__all__ = ["reverse_geocode", "regeo"]
