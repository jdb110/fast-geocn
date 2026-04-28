"""
坐标转换工具：WGS-84 ↔ GCJ-02 ↔ BD-09。

国内地图服务使用的坐标系：
- **WGS-84**：GPS 原生坐标系，我们的 GeoJSON 数据和 reverse_geocode 查询结果使用此坐标系
- **GCJ-02**（火星坐标系）：高德、腾讯地图使用的坐标系
- **BD-09**：百度地图使用的坐标系（在 GCJ-02 基础上再次加密）

转换算法基于开源实现，精度约 0.5~1 米。
"""

import math
from typing import Tuple

# 克拉索夫斯基椭球参数
_A = 6378245.0  # 半长轴
_EE = 0.00669342162296594323  # 偏心率平方

# 中国大陆大致范围
_LO_MIN, _LO_MAX = 72.0, 137.0
_LA_MIN, _LA_MAX = 0.0, 55.0


def _transform_lat(lng: float, lat: float) -> float:
    """GCJ-02 纬度偏移量计算。"""
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * math.pi) + 40.0 * math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * math.pi) + 320.0 * math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
    return ret


def _transform_lng(lng: float, lat: float) -> float:
    """GCJ-02 经度偏移量计算。"""
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * math.pi) + 20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * math.pi) + 40.0 * math.sin(lng / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * math.pi) + 300.0 * math.sin(lng / 30.0 * math.pi)) * 2.0 / 3.0
    return ret


def _is_out_of_china(lng: float, lat: float) -> bool:
    """判断坐标是否在中国境外（境外坐标无需纠偏）。"""
    return not (_LO_MIN <= lng <= _LO_MAX and _LA_MIN <= lat <= _LA_MAX)


def wgs84_to_gcj02(lng: float, lat: float) -> Tuple[float, float]:
    """WGS-84 → GCJ-02（火星坐标系）。

    Args:
        lng: WGS-84 经度。
        lat: WGS-84 纬度。

    Returns:
        (gcj_lng, gcj_lat)，境外坐标返回原值。
    """
    if _is_out_of_china(lng, lat):
        return (lng, lat)

    dlat = _transform_lat(lng - 105.0, lat - 35.0)
    dlng = _transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - _EE * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((_A * (1 - _EE)) / (magic * sqrtmagic) * math.pi)
    dlng = (dlng * 180.0) / (_A / sqrtmagic * math.cos(radlat) * math.pi)
    return (lng + dlng, lat + dlat)


def gcj02_to_wgs84(lng: float, lat: float) -> Tuple[float, float]:
    """GCJ-02 → WGS-84（迭代法，精度约 0.5 米）。

    Args:
        lng: GCJ-02 经度。
        lat: GCJ-02 纬度。

    Returns:
        (wgs_lng, wgs_lat)，境外坐标返回原值。
    """
    if _is_out_of_china(lng, lat):
        return (lng, lat)

    # 迭代求解：WGS = GCJ - offset(WGS)
    wgs_lng, wgs_lat = lng, lat
    for _ in range(5):  # 5 次迭代足够收敛
        gcj_lng, gcj_lat = wgs84_to_gcj02(wgs_lng, wgs_lat)
        wgs_lng += lng - gcj_lng
        wgs_lat += lat - gcj_lat
    return (wgs_lng, wgs_lat)


def gcj02_to_bd09(lng: float, lat: float) -> Tuple[float, float]:
    """GCJ-02 → BD-09（百度坐标系）。

    Args:
        lng: GCJ-02 经度。
        lat: GCJ-02 纬度。

    Returns:
        (bd_lng, bd_lat)。
    """
    x = lng
    y = lat
    z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * math.pi)
    theta = math.atan2(y, x) + 0.000003 * math.cos(x * math.pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return (bd_lng, bd_lat)


def bd09_to_gcj02(lng: float, lat: float) -> Tuple[float, float]:
    """BD-09 → GCJ-02。

    Args:
        lng: BD-09 经度。
        lat: BD-09 纬度。

    Returns:
        (gcj_lng, gcj_lat)。
    """
    x = lng - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * math.pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * math.pi)
    gcj_lng = z * math.cos(theta)
    gcj_lat = z * math.sin(theta)
    return (gcj_lng, gcj_lat)


def wgs84_to_bd09(lng: float, lat: float) -> Tuple[float, float]:
    """WGS-84 → BD-09（一步转换）。

    Args:
        lng: WGS-84 经度。
        lat: WGS-84 纬度。

    Returns:
        (bd_lng, bd_lat)。
    """
    gcj_lng, gcj_lat = wgs84_to_gcj02(lng, lat)
    return gcj02_to_bd09(gcj_lng, gcj_lat)


def bd09_to_wgs84(lng: float, lat: float) -> Tuple[float, float]:
    """BD-09 → WGS-84（一步转换）。

    Args:
        lng: BD-09 经度。
        lat: BD-09 纬度。

    Returns:
        (wgs_lng, wgs_lat)。
    """
    gcj_lng, gcj_lat = bd09_to_gcj02(lng, lat)
    return gcj02_to_wgs84(gcj_lng, gcj_lat)


__all__ = [
    "wgs84_to_gcj02",
    "gcj02_to_wgs84",
    "gcj02_to_bd09",
    "bd09_to_gcj02",
    "wgs84_to_bd09",
    "bd09_to_wgs84",
]
