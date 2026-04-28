# Fast-GeoCN

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**超轻量离线中国行政区划逆地理编码** — 仅依赖 `shapely`，开箱即用。

## 特性

- ⚡ **极致轻量** — 仅依赖 `shapely`，无 pandas/geopandas，安装体积约 15 MB
- 🚀 **极速查询** — 运行时自动生成 pickle 缓存 + STRtree 空间索引 + PreparedGeometry 精确匹配，二次查询 **亚毫秒级**
- 🔌 **兼容** — 兼容 `regeo(lng, lat)` 函数签名
- 📦 **开箱即用** — 内置中国省市县三级 GeoJSON 数据，pip install 即可使用
- 🛠 **自动缓存** — 首次查询自动转为 pickle 缓存，后续秒级响应

## 快速开始

### 1. 安装

```bash
pip install fast-geocn
```

### 2. 查询

```python
from fast_geocn import regeo

result = regeo(114.0579, 22.5431)  # (经度, 纬度)
print(result)
# {'status': 1, 'Info': 'Successfully retrieved address.',
#  'address': {'province': '广东省', 'province_code': '440000',
#              'city': '深圳市', 'city_code': '440300',
#              'district': '南山区', 'district_code': '440305'}}
```

## API 文档

### `regeo(lng, lat)`

与 PyGeoCN 完全兼容的逆地理编码函数。

| 参数 | 类型 | 说明 |
|------|------|------|
| `lng` | `float` | 经度 (WGS-84) |
| `lat` | `float` | 纬度 (WGS-84) |

**返回**：包含 `status`、`Info`、`address` 的字典。

### `reverse_geocode(lat, lon, data_dir=None)`

增强版逆地理编码函数，支持指定数据目录。

### `fast-geocn-prepare <geojson_dir> <output_dir>`

CLI 工具，将 GeoJSON 目录转为 pickle 缓存。

## 性能

| 指标 | 耗时 |
|------|------|
| 首次查询（含 GeoJSON 解析 + 缓存生成） | ~3.6 s |
| 二次查询（直接读 pickle 缓存） | **~1.7 ms** |
| 内存常驻后单次查询 | **~0.2 ms** |

## 数据源推荐

| 数据源 | 说明 |
|--------|------|
| [DataV.GeoAtlas](https://datav.aliyun.com) | 阿里云开源中国行政区划数据 |
| [geojson.cn](https://geojson.cn) | 天地图省市县 GeoJSON，带审图号 |
| [cn-atlas](https://shengshixian.com) | 基于高德地图 API 的 TopoJSON/GeoJSON |

## 依赖

- `shapely >= 2.0`

## 许可证

[MIT](LICENSE)
