"""basic_signature.py
轻量级 SpatialSignature 数据结构以及辅助函数

仅依赖 AI2-THOR 元数据 (AABB + rotation + objectId)。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any
import math
import numpy as np

__all__ = [
    "SpatialSignature",
    "rotation_matrix_y",
]

def rotation_matrix_y(angle_deg: float) -> np.ndarray:
    """生成绕 Y 轴旋转的 3×3 矩阵 (右手坐标系)。"""
    theta = math.radians(angle_deg)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    return np.array(
        [
            [cos_t, 0.0, sin_t],
            [0.0, 1.0, 0.0],
            [-sin_t, 0.0, cos_t],
        ],
        dtype=float,
    )


@dataclass
class SpatialSignature:
    """轻量级空间签名.

    Attributes
    ----------
    object_id : str
        AI2-THOR 为该实例生成的唯一 ID。
    object_type : str
        e.g. "Sofa", "Book".
    center : np.ndarray, shape (3,)
        物体 AABB 中心 (世界坐标系)。
    size : np.ndarray, shape (3,)
        AABB 尺寸 (w, h, d)。
    rotation : np.ndarray, shape (3,3)
        物体局部坐标系到世界坐标系的旋转矩阵 (仅 Y 轴旋转，来自元数据)。
    meta : Dict[str,Any]
        其余未使用的元数据，备查。
    """

    object_id: str
    object_type: str
    center: np.ndarray
    size: np.ndarray
    rotation: np.ndarray
    meta: Dict[str, Any] = field(default_factory=dict)

    # 便捷属性
    @property
    def half_size(self) -> np.ndarray:
        return self.size / 2.0

    # ---------- 工厂方法 ----------
    @classmethod
    def from_metadata(cls, obj_meta: Dict[str, Any]) -> "SpatialSignature":
        """从 AI2-THOR 返回的 object 元数据创建签名"""
        # axisAlignedBoundingBox 提供 center & size
        aabb = obj_meta.get("axisAlignedBoundingBox", {})
        center_dict = aabb.get("center", {})
        size_dict = aabb.get("size", {})

        center = np.array([
            center_dict.get("x", 0.0),
            center_dict.get("y", 0.0),
            center_dict.get("z", 0.0),
        ])
        size = np.array([
            size_dict.get("x", 0.0),
            size_dict.get("y", 0.0),
            size_dict.get("z", 0.0),
        ])

        # rotation 字段只有 y 分量, 其余默认为 0
        rotation_y_deg = obj_meta.get("rotation", {}).get("y", 0.0)
        rot_mat = rotation_matrix_y(rotation_y_deg)

        return cls(
            object_id=obj_meta.get("objectId", "unknown"),
            object_type=obj_meta.get("objectType", "unknown"),
            center=center,
            size=size,
            rotation=rot_mat,
            meta={
                "distance": obj_meta.get("distance", None),
                "visible": obj_meta.get("visible", None),
            },
        )

    # ---------- 坐标转换 ----------
    def world_to_local(self, points: np.ndarray) -> np.ndarray:
        """世界坐标 -> 物体局部坐标"""
        # 平移
        rel = points - self.center
        # 仅 Y 轴旋转, rotation 是局部->世界, 因此取转置
        return rel @ self.rotation.T

    def local_to_world(self, local_pts: np.ndarray) -> np.ndarray:
        """物体局部坐标 -> 世界坐标"""
        return (local_pts @ self.rotation) + self.center

    # ---------- 区域中心快速计算 ----------
    def region_center(self, local_offset: np.ndarray) -> np.ndarray:
        """给定局部坐标偏移(0~1 之间), 返回世界坐标中心

        Parameters
        ----------
        local_offset : np.ndarray, shape (3,)
            在局部坐标系中相对于中心的比例偏移, (-0.5~0.5)。
        """
        assert local_offset.shape == (3,)
        local = local_offset * self.size
        return self.local_to_world(local) 