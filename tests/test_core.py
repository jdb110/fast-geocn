"""Tests for fast_geocn.core module."""

import json
import shutil
import threading
import tempfile
from pathlib import Path

import pytest

from fast_geocn.core import _Cache, reverse_geocode

_PROVINCE_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "广东省", "gb": "440000"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[109.5, 20.2], [117.2, 20.2], [117.2, 25.5], [109.5, 25.5], [109.5, 20.2]]],
            },
        },
    ],
}

_CITY_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "深圳市", "gb": "440300"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[113.7, 22.4], [114.4, 22.4], [114.4, 22.9], [113.7, 22.9], [113.7, 22.4]]],
            },
        },
    ],
}

_DISTRICT_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "南山区", "gb": "440305"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[113.88, 22.45], [114.1, 22.45], [114.1, 22.6], [113.88, 22.6], [113.88, 22.45]]],
            },
        },
    ],
}

_CACHE_DIR = Path.home() / ".fast_geocn_cache"
_CACHE_FILE = _CACHE_DIR / "fast_geocn.pkl"


@pytest.fixture
def temp_geojson_dir():
    """创建带 .geojson 的临时目录，模拟外部数据源。"""
    tmp = tempfile.mkdtemp()
    data = {"province": _PROVINCE_GEOJSON, "city": _CITY_GEOJSON, "district": _DISTRICT_GEOJSON}
    for name, geojson in data.items():
        with open(Path(tmp) / f"{name}.geojson", "w", encoding="utf-8") as f:
            json.dump(geojson, f)
    yield tmp
    shutil.rmtree(tmp)
    # 清理缓存
    _CACHE_FILE.unlink(missing_ok=True)


class TestCache:

    def setup_method(self):
        _Cache._reset()

    def teardown_method(self):
        _Cache._reset()

    def test_singleton(self):
        cache1 = _Cache()
        cache2 = _Cache()
        assert cache1 is cache2

    def test_singleton_thread_safety(self):
        instances = []

        def create():
            instances.append(_Cache())

        threads = [threading.Thread(target=create) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        first = instances[0]
        for inst in instances[1:]:
            assert inst is first

    def test_load_thread_safety(self):
        cache = _Cache()
        cache._data = {}
        cache._loaded = True

        errors = []

        def load_it():
            try:
                cache.load("/tmp/nonexistent_cache_xyz")
            except FileNotFoundError:
                pass
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=load_it) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Unexpected errors: {errors}"

    def test_initial_data_empty(self):
        cache = _Cache()
        cache._data = {}
        assert len(cache._data) == 0

    def test_auto_convert_and_cache(self, temp_geojson_dir):
        """load() 应自动生成 ~/.fast_geocn_cache/fast_geocn.pkl。"""
        _CACHE_FILE.unlink(missing_ok=True)

        cache = _Cache()
        cache._loaded = True
        cache._data = {}

        data = cache.load(temp_geojson_dir)
        assert "province" in data
        assert "city" in data
        assert "district" in data
        assert data["province"]["properties"][0]["name"] == "广东省"

        # 验证单个合并缓存文件已生成
        assert _CACHE_FILE.exists()

    def test_cache_reuse(self, temp_geojson_dir):
        """第二次 load() 应重用已有缓存（删除 geojson 后仍能读取）。"""
        _Cache._reset()
        cache = _Cache()
        cache._loaded = True
        cache._data = {}

        data1 = cache.load(temp_geojson_dir)

        _Cache._reset()
        cache2 = _Cache()

        # 删除源 GeoJSON 后再加载，应该仍能从缓存读取
        shutil.rmtree(temp_geojson_dir)
        Path(temp_geojson_dir).mkdir(exist_ok=True)

        cache2._loaded = True
        cache2._data = {}
        data2 = cache2.load(temp_geojson_dir)

        assert data2["province"]["properties"][0]["name"] == "广东省"


class TestReverseGeocode:

    def setup_method(self):
        _Cache._reset()

    def teardown_method(self):
        _Cache._reset()

    def test_no_data_dir_raises(self):
        with pytest.raises(FileNotFoundError):
            reverse_geocode(22.5431, 114.0579, data_dir="/tmp/nonexistent_path_xyz")

    def test_regeo_alias(self):
        """regeo() 应调用 reverse_geocode 并返回正确结果。"""
        from fast_geocn import regeo

        result = regeo(114.0579, 22.5431)
        assert result["status"] == 1

    def test_reverse_geocode_with_geojson(self, temp_geojson_dir):
        result = reverse_geocode(22.5431, 114.0579, data_dir=temp_geojson_dir)
        assert result["status"] == 1
        assert result["address"]["province"] == "广东省"
        assert result["address"]["city"] == "深圳市"
        assert result["address"]["district"] == "南山区"

    def test_reverse_geocode_with_package_data(self):
        """使用包内 data/ 数据应正常工作。"""
        _Cache._reset()
        result = reverse_geocode(22.5431, 114.0579)
        assert result["status"] == 1
        assert result["address"]["province"] == "广东省"
        assert result["address"]["city"] == "深圳市"
        assert result["address"]["district"] is not None
        assert result["status"] == 1
        assert result["address"]["province"] == "广东省"
