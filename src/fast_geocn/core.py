"""
Fast-GeoCN 核心模块：超轻量离线逆地理编码。

仅依赖 shapely，无 pandas/geopandas。
包内 data/ 目录存放 GeoJSON 源文件（pip 可见）。
首次运行时自动转换为 pickle 缓存到 ~/.fast_geocn_cache/fast_geocn.pkl，
后续直接读 pickle 大幅提速。

三重优化：
1. pickle 本地缓存，二次加载零解析开销
2. STRtree 空间索引快速过滤候选多边形
3. PreparedGeometry 高效精确匹配

线程安全：_Cache 使用双重检查锁（double-checked locking）保证单例。
"""

from __future__ import annotations

import json
import pickle
import threading
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from shapely.geometry import Point, shape
from shapely.geometry.base import BaseGeometry
from shapely.prepared import PreparedGeometry, prep
from shapely.strtree import STRtree

from . import coord

# 包内 GeoJSON 源数据目录（pip 安装时自带）
_PACKAGE_DATA = Path(__file__).parent / "data"

# 用户级缓存目录（运行时自动生成）
_CACHE_DIR = Path.home() / ".fast_geocn_cache"
_CACHE_PATH = _CACHE_DIR / "fast_geocn.pkl"

# 三级行政区划
_LEVEL_FILES = {
    "province": "province.geojson",
    "city": "city.geojson",
    "district": "district.geojson",
}


def _load_geojson(geojson_path: Path) -> Tuple[Tuple[BaseGeometry, ...], List[dict], STRtree]:
    """加载 GeoJSON，返回 (geometries, properties, tree)。"""
    with open(geojson_path, encoding="utf-8") as f:
        raw = json.load(f)

    geometries: List[BaseGeometry] = []
    props_list: List[dict] = []
    for feat in raw["features"]:
        geometries.append(shape(feat["geometry"]))
        props_list.append(feat["properties"])

    tree = STRtree(geometries)
    return (tuple(geometries), props_list, tree)


def _get_geojson_path(level: str, data_dir: Optional[Path] = None) -> Path:
    """获取 GeoJSON 源文件路径，兼容 level.geojson 和 china_level.geojson。"""
    base = data_dir if data_dir else _PACKAGE_DATA
    path = base / _LEVEL_FILES[level]
    return path if path.exists() else base / f"china_{_LEVEL_FILES[level]}"


def _ensure_cache(data_dir: Optional[Path] = None) -> Dict[str, dict]:
    """确保合并缓存就绪。

    检查 fast_geocn.pkl 是否存在且未过期（对比所有 .geojson 的 mtime）。
    若需重建，一次性解析所有 .geojson 写入单个缓存文件。
    """
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # 缓存存在且任何源文件都未更新 → 直接加载
    if _CACHE_PATH.exists():
        cache_mtime = _CACHE_PATH.stat().st_mtime
        need_rebuild = False
        for level in _LEVEL_FILES:
            src = _get_geojson_path(level, data_dir)
            if src.exists() and src.stat().st_mtime > cache_mtime:
                need_rebuild = True
                break

        if not need_rebuild:
            with open(_CACHE_PATH, "rb") as f:
                return pickle.load(f)

    # 重建缓存（需所有源文件存在）
    all_data: Dict[str, dict] = {}
    for level in _LEVEL_FILES:
        src = _get_geojson_path(level, data_dir)
        if not src.exists():
            if data_dir:
                raise FileNotFoundError(f"数据文件缺失: {src}")
            raise FileNotFoundError(f"包内数据缺失: {src}\n请重装 fast-geocn。")
        geometries, properties, tree = _load_geojson(src)
        all_data[level] = {
            "geometries": geometries,
            "properties": properties,
            "tree": tree,
        }

    with open(_CACHE_PATH, "wb") as f:
        pickle.dump(all_data, f, protocol=pickle.HIGHEST_PROTOCOL)
    return all_data


class _Cache:
    """线程安全的单例：数据仅加载一次到内存。

    优先从 ~/.fast_geocn_cache/fast_geocn.pkl 加载（极快），
    若缓存缺失或过期则自动从包内 .geojson 重建。
    """

    _instance: Optional[_Cache] = None
    _singleton_lock: threading.Lock = threading.Lock()

    def __new__(cls) -> _Cache:
        if cls._instance is None:
            with cls._singleton_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._loaded = False
                    cls._instance._data: Dict[str, dict] = {}
                    cls._instance._load_lock = threading.Lock()
        return cls._instance

    def __init__(self) -> None:
        if self._loaded:
            return
        with self._singleton_lock:
            if self._loaded:
                return
            self._loaded = True

    @classmethod
    def _reset(cls) -> None:
        """重置单例（仅用于测试）。"""
        cls._instance = None

    def load(self, data_dir: Optional[str] = None) -> Dict[str, dict]:
        """加载数据（线程安全）。

        优先从 ~/.fast_geocn_cache/fast_geocn.pkl 加载。
        若缓存缺失或 GeoJSON 更新则自动重建。

        Args:
            data_dir: 可选，外部 GeoJSON 目录。为 None 则使用包内 data/。

        Returns:
            {level: {"geometries": tuple, "properties": list, "tree": STRtree}}
        """
        if self._data:
            return self._data

        with self._load_lock:
            if self._data:
                return self._data

            dir_path = Path(data_dir) if data_dir else None
            self._data = _ensure_cache(dir_path)
            return self._data


@lru_cache(maxsize=8192)
def _get_prepared(geometries: tuple, idx: int) -> PreparedGeometry:
    """缓存 PreparedGeometry，避免重复构建。"""
    return prep(geometries[idx])


def reverse_geocode(
    lat: float,
    lon: float,
    data_dir: Optional[str] = None,
    source_crs: str = "wgs84",
) -> Dict[str, Any]:
    """离线逆地理编码。

    首次调用时自动将包内 .geojson 转为 ~/.fast_geocn_cache/fast_geocn.pkl 缓存。

    Args:
        lat: 纬度。
        lon: 经度。
        data_dir: 可选，外部 GeoJSON 数据目录。为 None 则使用包内内置数据。
        source_crs: 输入坐标的坐标系。可选值:
            - "wgs84" (默认): 无需转换
            - "gcj02": 火星坐标系（高德/腾讯地图），自动转 WGS-84
            - "bd09": 百度坐标系，自动转 WGS-84

    Returns:
        {
            "status": 1 或 0,
            "Info": "...",
            "address": { ... }
        }
    """
    cache = _Cache().load(data_dir)

    # 坐标系自动转换
    if source_crs == "gcj02":
        wgs_lon, wgs_lat = coord.gcj02_to_wgs84(lon, lat)
    elif source_crs == "bd09":
        wgs_lon, wgs_lat = coord.bd09_to_wgs84(lon, lat)
    elif source_crs == "wgs84":
        wgs_lon, wgs_lat = lon, lat
    else:
        raise ValueError(f"不支持的坐标系: {source_crs}，可选: wgs84, gcj02, bd09")

    point = Point(wgs_lon, wgs_lat)

    result: Dict[str, Any] = {
        "status": 1,
        "Info": "Successfully retrieved address.",
        "address": {
            "province": None, "province_code": None,
            "city": None, "city_code": None,
            "district": None, "district_code": None,
        },
    }

    for level in ("province", "city", "district"):
        payload = cache[level]
        geometries: tuple = payload["geometries"]
        properties: list = payload["properties"]
        tree: STRtree = payload["tree"]

        candidate_idxs = tree.query(point, predicate="intersects")
        if len(candidate_idxs) == 0:
            result["status"] = 0
            result["Info"] = "Coordinates outside China."
            break

        hit = False
        for idx in candidate_idxs:
            if _get_prepared(geometries, idx).contains(point):
                rec = properties[idx]
                if level == "province":
                    result["address"]["province"] = rec.get("name")
                    result["address"]["province_code"] = rec.get("gb")
                elif level == "city":
                    result["address"]["city"] = rec.get("name")
                    result["address"]["city_code"] = rec.get("gb")
                else:
                    result["address"]["district"] = rec.get("name")
                    result["address"]["district_code"] = rec.get("gb")
                hit = True
                break

        if not hit:
            result["status"] = 0
            result["Info"] = f"Address not found at {level} level."
            break

    return result


def regeo(lng: float, lat: float, source_crs: str = "wgs84") -> Dict[str, Any]:
    """兼容接口：先经度后纬度。

    Args:
        lng: 经度。
        lat: 纬度。
        source_crs: 输入坐标的坐标系。默认 "wgs84"，可选 "gcj02", "bd09"。

    Returns:
        地址信息字典。
    """
    return reverse_geocode(lat, lng, source_crs=source_crs)
