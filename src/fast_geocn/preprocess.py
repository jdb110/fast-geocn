"""
数据预处理工具：将 GeoJSON 转为 pickle 缓存。

用法：
    fast-geocn-prepare <geojson_dir> <output_dir>

注意：通常无需手动调用。fast-geocn 首次查询时会自动将包内
data/ 下的 .geojson 转为 ~/.fast_geocn_cache/*.pkl 缓存。

此工具用于以下场景：
- 使用自定义 GeoJSON 数据而非包内内置数据
- 手动强制重建本地缓存
"""

import json
import pickle
import sys
from pathlib import Path

from shapely.geometry import shape
from shapely.strtree import STRtree


def geojson_to_pkl(geojson_path: Path, pkl_path: Path) -> None:
    """将单个 GeoJSON 文件转为 .pkl 缓存。

    Args:
        geojson_path: 输入的 GeoJSON 文件路径。
        pkl_path: 输出的 .pkl 文件路径。
    """
    with open(geojson_path, encoding="utf-8") as f:
        data = json.load(f)

    geometries = []
    props_list = []
    for feat in data["features"]:
        geom = shape(feat["geometry"])
        geometries.append(geom)
        props_list.append(feat["properties"])

    tree = STRtree(geometries)

    payload = {
        "geometries": tuple(geometries),
        "properties": props_list,
        "tree": tree,
    }

    with open(pkl_path, "wb") as f:
        pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"[OK] {geojson_path.name} -> {pkl_path.name} ({len(geometries)} records)")


def main() -> None:
    """命令行入口。"""
    if len(sys.argv) < 3:
        print("用法: fast-geocn-prepare <geojson_dir> <output_dir>")
        print("示例: fast-geocn-prepare ./my_geojson_dir ./my_cache")
        print()
        print("警告：通常无需手动调用，fast-geocn 首次查询时会自动生成缓存。")
        sys.exit(1)

    geojson_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)

    geojson_files = sorted(geojson_dir.glob("*.geojson"))
    if not geojson_files:
        print(f"[WARN] {geojson_dir} 下未找到 .geojson 文件")
        return

    for src in geojson_files:
        key = src.stem.replace("china_", "", 1)
        geojson_to_pkl(src, output_dir / f"{key}.pkl")

    print(f"提示：手动转换完成。通常无需手动调用，fast-geocn 首次查询时自动生成缓存。")


if __name__ == "__main__":
    main()
