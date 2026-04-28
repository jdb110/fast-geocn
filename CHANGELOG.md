# Changelog

## 1.0.0 (2026-04-28)

### ✨ Features

- 初始版本发布
- 仅依赖 shapely，零 pandas/geopandas，极致轻量
- 单例缓存，程序生命周期内仅加载一次数据
- STRtree 空间索引 + PreparedGeometry 加速多边形查询
- 数据预处理 CLI 工具：GeoJSON → pickle 缓存
- 兼容 `regeo(lng, lat)` 接口
- 运行首次查询时自动解析包内 GeoJSON 并缓存至 ~/.fast_geocn_cache/
- 二次查询亚毫秒级（内存缓存 + STRtree + PreparedGeometry）
