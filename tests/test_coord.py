"""Tests for fast_geocn.coord module."""

from fast_geocn.coord import (
    wgs84_to_gcj02,
    gcj02_to_wgs84,
    gcj02_to_bd09,
    bd09_to_gcj02,
    wgs84_to_bd09,
    bd09_to_wgs84,
)

# 深圳市政府的 WGS-84 坐标（约）
SHENZHEN_WGS = (114.0579, 22.5431)


class TestWgs84Gcj02:
    """WGS-84 ↔ GCJ-02 互转测试。"""

    def test_wgs84_to_gcj02_offset(self):
        """WGS-84 转 GCJ-02 应该有偏移（中国境内）。"""
        gcj_lng, gcj_lat = wgs84_to_gcj02(*SHENZHEN_WGS)
        assert gcj_lng != SHENZHEN_WGS[0]
        assert gcj_lat != SHENZHEN_WGS[1]

    def test_gcj02_to_wgs84_recovery(self):
        """GCJ-02 → WGS-84 应该能恢复原值（误差 < 1m）。"""
        gcj_lng, gcj_lat = wgs84_to_gcj02(*SHENZHEN_WGS)
        wgs_lng, wgs_lat = gcj02_to_wgs84(gcj_lng, gcj_lat)
        # 误差应小于 0.00001°（约 1 米）
        assert abs(wgs_lng - SHENZHEN_WGS[0]) < 0.00001
        assert abs(wgs_lat - SHENZHEN_WGS[1]) < 0.00001

    def test_roundtrip_wgs84_gcj02(self):
        """WGS-84 → GCJ-02 → WGS-84 往返误差 < 1m。"""
        for lng, lat in [
            (114.0579, 22.5431),
            (116.4074, 39.9042),
            (121.4737, 31.2304),
            (87.6168, 43.8256),
        ]:
            gcj_lng, gcj_lat = wgs84_to_gcj02(lng, lat)
            wgs_lng, wgs_lat = gcj02_to_wgs84(gcj_lng, gcj_lat)
            assert abs(wgs_lng - lng) < 0.00001
            assert abs(wgs_lat - lat) < 0.00001

    def test_out_of_china_no_offset(self):
        """境外坐标不应有偏移。"""
        for lng, lat in [(0.0, 0.0), (-122.4, 37.8), (151.2, -33.9)]:
            gcj_lng, gcj_lat = wgs84_to_gcj02(lng, lat)
            assert gcj_lng == lng
            assert gcj_lat == lat


class TestGcj02Bd09:
    """GCJ-02 ↔ BD-09 互转测试。"""

    def test_roundtrip_gcj02_bd09(self):
        """GCJ-02 → BD-09 → GCJ-02 往返恢复。"""
        gcj_lng, gcj_lat = wgs84_to_gcj02(*SHENZHEN_WGS)
        bd_lng, bd_lat = gcj02_to_bd09(gcj_lng, gcj_lat)
        back_lng, back_lat = bd09_to_gcj02(bd_lng, bd_lat)
        assert abs(back_lng - gcj_lng) < 0.001
        assert abs(back_lat - gcj_lat) < 0.001


class TestWgs84Bd09:
    """WGS-84 ↔ BD-09 一步转换测试。"""

    def test_roundtrip_wgs84_bd09(self):
        """WGS-84 → BD-09 → WGS-84 往返恢复（误差 < 2m）。"""
        bd_lng, bd_lat = wgs84_to_bd09(*SHENZHEN_WGS)
        wgs_lng, wgs_lat = bd09_to_wgs84(bd_lng, bd_lat)
        assert abs(wgs_lng - SHENZHEN_WGS[0]) < 0.00002
        assert abs(wgs_lat - SHENZHEN_WGS[1]) < 0.00002


class TestIsOutOfChina:
    """境外判断测试。"""

    def test_china_coords(self):
        from fast_geocn.coord import _is_out_of_china
        assert not _is_out_of_china(114.0579, 22.5431)
        assert not _is_out_of_china(116.4074, 39.9042)
        assert not _is_out_of_china(121.4737, 31.2304)

    def test_non_china_coords(self):
        from fast_geocn.coord import _is_out_of_china
        assert _is_out_of_china(0.0, 0.0)
        assert _is_out_of_china(-122.4, 37.8)
        assert _is_out_of_china(151.2, -33.9)
