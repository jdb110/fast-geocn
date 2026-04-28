# Changelog

## 1.1.0 (2026-04-28)

### ✨ Features

- 新增坐标转换模块 `coord.py`：WGS-84 ↔ GCJ-02 ↔ BD-09 互转
- `regeo()` / `reverse_geocode()` 新增 `source_crs` 参数，自动转换输入坐标
- 境外坐标判断优化
- 代码质量清理：移除 `from __future__ import annotations`、死代码、补充断言

## 1.0.0 (2026-04-28)

### ✨ Features

- 初始版本发布
- 仅依赖 shapely，零 pandas/geopandas，极致轻量
- 单例缓存，程序生命周期内仅加载一次数据
- STRtree 空间索引 + PreparedGeometry 加速多边形查询
- 数据预处理 CLI 工具：GeoJSON → pickle 缓存
- 兼容 `regeo(lng, lat)` 接口
- 运行首次查询时自动解析包内 GeoJSON 并缓存至 ~/.fast_geocn_cache/
- 二次查询亚毫秒级
