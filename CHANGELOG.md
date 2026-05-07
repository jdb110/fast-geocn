# Changelog

## 1.1.2 (2026-05-07)

### 🐛 Bug Fixes

- 修复 `_Cache` 类体内自引用类型注解引发的 `NameError`（`from __future__ import annotations`）

## 1.1.1 (2026-04-29)

### 📝 Docs

- 修复 README 文档与实际不符的问题：安装体积、性能描述、坐标系说明
- README 示例坐标更换为 (104.96, 27.43)（云南省昭通市镇雄县）

## 1.1.0 (2026-04-28)

### ✨ Features

- 新增坐标转换模块 `coord.py`：WGS-84 ↔ GCJ-02 ↔ BD-09 互转
- `regeo()` / `reverse_geocode()` 新增 `source_crs` 参数，支持 WGS-84 / GCJ-02 / BD-09 输入转换
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
- 二次查询毫秒级（~1.7 ms），内存常驻后 ~0.2 ms
