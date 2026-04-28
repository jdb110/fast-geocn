"""pytest fixtures for fast-geocn tests."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_data_dir() -> str:
    """返回测试用样本数据目录。

    若 tests/data/ 存在则使用，否则跳过需要数据的测试。
    """
    data_dir = Path(__file__).parent / "data"
    if data_dir.is_dir():
        return str(data_dir)
    pytest.skip("测试数据目录 tests/data/ 不存在，请先准备样本数据")

