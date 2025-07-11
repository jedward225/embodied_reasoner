"""region_utils.py
根据 AABB 快速切分常见大型物体的语义子区。
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple
import numpy as np
from .basic_signature import SpatialSignature


class RegionSchema(str, Enum):
    SOFA = "sofa"
    TABLE = "table"
    CABINET = "cabinet"


def _sofa_rules(sig: SpatialSignature) -> Dict[str, np.ndarray]:
    """返回每个子区中心 (世界坐标)。"""
    # 局部坐标快捷变量 (-0.5~0.5)
    half = sig.half_size
    # y 取 seat top
    seat_y = 0.0  # 局部中心
    # 左右区分依据 x
    offsets = {
        "seat": np.array([0.0, seat_y, 0.0]),
        "left_arm": np.array([-0.4, 0.25, 0.0]),
        "right_arm": np.array([0.4, 0.25, 0.0]),
        "back": np.array([0.0, 0.4, 0.4]),
    }
    return {k: sig.region_center(v) for k, v in offsets.items()}


def _table_rules(sig: SpatialSignature) -> Dict[str, np.ndarray]:
    offsets = {
        "top_center": np.array([0.0, 0.5, 0.0]),
        "left_edge": np.array([-0.45, 0.5, 0.0]),
        "right_edge": np.array([0.45, 0.5, 0.0]),
        "front_edge": np.array([0.0, 0.5, 0.45]),
        "back_edge": np.array([0.0, 0.5, -0.45]),
    }
    return {k: sig.region_center(v) for k, v in offsets.items()}


def _cabinet_rules(sig: SpatialSignature) -> Dict[str, np.ndarray]:
    offsets = {
        "top_shelf": np.array([0.0, 0.4, 0.0]),
        "middle_shelf": np.array([0.0, 0.0, 0.0]),
        "bottom_shelf": np.array([0.0, -0.4, 0.0]),
    }
    return {k: sig.region_center(v) for k, v in offsets.items()}


_RULE_DISPATCH = {
    RegionSchema.SOFA: _sofa_rules,
    RegionSchema.TABLE: _table_rules,
    RegionSchema.CABINET: _cabinet_rules,
}


def slice_aabb(signature: SpatialSignature, schema: str | RegionSchema) -> Dict[str, np.ndarray]:
    """根据 schema 返回子区中心点 (世界坐标) 字典。"""
    if isinstance(schema, str):
        schema = RegionSchema(schema.lower())
    if schema not in _RULE_DISPATCH:
        raise ValueError(f"Unsupported schema: {schema}")
    return _RULE_DISPATCH[schema](signature) 