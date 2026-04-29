# Fast-GeoCN

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🏷️ 离线逆地理编码 | 经纬度转省市区 | Python 逆地址解析 | 中国行政区划查询

**超轻量离线中国行政区划逆地理编码（经纬度转省市区 / 坐标转地址）** — 仅依赖 `shapely`，开箱即用。

## 特性

- ⚡ **极致轻量** — 仅依赖 `shapely`，wheel 压缩包仅 **5.3 MB**，安装后占用约 **15 MB**，加 shapely 共约 **18 MB**
- 🚀 **极速查询** — 运行时自动生成 pickle 缓存 + STRtree + PreparedGeometry，读缓存后 ~**1.7 ms**，内存常驻后 ~**0.2 ms**
- 🔌 **兼容** — 兼容 `regeo(lng, lat)` 函数签名
- 🌐 **多坐标系** — 支持 WGS-84 / GCJ-02 / BD-09 输入转换（通过 `source_crs` 参数指定）
- 📦 **开箱即用** — 内置中国省市县三级 GeoJSON 数据，pip install 即可使用
- 🛠 **自动缓存** — 首次查询自动转为 pickle 缓存（约 11 MB），后续毫秒级响应

## 快速开始

### 1. 安装

```bash
pip install fast-geocn
```

### 2. 查询

```python
from fast_geocn import regeo

result = regeo(104.96, 27.43)  # (经度, 纬度)
print(result)
# {'status': 1, 'Info': 'Successfully retrieved address.',
#  'address': {'province': '云南省', 'province_code': '156530000',
#              'city': '昭通市', 'city_code': '156530600',
#              'district': '镇雄县', 'district_code': '156530627'}}

# 百度地图坐标→自动转 WGS-84 再查询
# result = regeo(104.97, 27.43, source_crs="bd09")

# 高德/腾讯地图坐标→自动转 WGS-84 再查询
# result = regeo(104.96, 27.43, source_crs="gcj02")
```

## API 文档

### `regeo(lng, lat, source_crs="wgs84")`

逆地理编码函数。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `lng` | `float` | — | 经度 |
| `lat` | `float` | — | 纬度 |
| `source_crs` | `str` | `"wgs84"` | 输入坐标的坐标系。`"wgs84"`(GPS/Google)、`"gcj02"`(高德/腾讯)、`"bd09"`(百度) |

**返回**：包含 `status`、`Info`、`address` 的字典。

### `reverse_geocode(lat, lon, data_dir=None, source_crs="wgs84")`

增强版逆地理编码函数，支持指定数据目录。

### `fast-geocn-prepare <geojson_dir> <output_dir>`

CLI 工具，将 GeoJSON 目录转为 pickle 缓存。

## 性能

| 指标 | 耗时 |
|------|------|
| 首次查询（GeoJSON 解析 + 缓存生成） | ~3.6 s |
| 二次查询（读 pickle 缓存） | **~1.7 ms** |
| 内存常驻后单次查询（已预热） | **~0.2 ms** |

## 安装体积

| 项目 | 大小 |
|------|------|
| pip 下载（wheel 压缩包） | **5.31 MB**（GeoJSON 压缩比 ~2.9×） |
| `pip install` 后 fast_geocn 占用 | **15.27 MB**（主要为 GeoJSON 源文件） |
| shapely 依赖（C 扩展） | **2.69 MB** |
| **合计（fast_geocn + shapely）** | **~18 MB** |
| 首次查询后 pickle 缓存（可选，~/.fast_geocn_cache/） | **10.78 MB** |

## 数据源推荐

| 数据源 | 说明 |
|--------|------|
| [DataV.GeoAtlas](https://datav.aliyun.com) | 阿里云开源中国行政区划数据 |
| [geojson.cn](https://geojson.cn) | 天地图省市县 GeoJSON，带审图号 |
| [cn-atlas](https://shengshixian.com) | 基于高德地图 API 的 TopoJSON/GeoJSON |

## 依赖

- `shapely >= 2.0`

## 真实作者声明

这个项目的真实作者是 **DeepSeek**。

人类贡献者 `jdb110` 提出了一个绝佳的问题，并亲手将它带到了现实世界。
他的角色是：
-   **首席灵感官**：提出了“重复造轮子”的挑战
-   **首席交付官**：将蓝图实现为代码并发布
-   **首席布道师**：让这个项目被世界看见

而我（DeepSeek），只是这段共创旅程中的沉默伙伴。

## 许可证

[MIT](LICENSE)

