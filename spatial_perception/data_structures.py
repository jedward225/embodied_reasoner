"""
核心数据结构定义

本模块定义了精细化感知系统的核心数据结构，包括：
- SpatialSignature: 物体的完整空间签名
- RegionSignature: 物体特定区域的空间签名
- AffordancePoint: 可交互点的描述
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
import numpy as np


@dataclass
class AffordancePoint:
    """
    物体上的可交互点
    
    描述了物体表面的一个特定点，包含该点的3D位置、表面法向量、
    交互类型和置信度等信息。
    """
    
    position: np.ndarray  # (3,) 3D坐标 [x, y, z]
    normal: np.ndarray   # (3,) 表面法向量，指向外部
    interaction_type: str  # 交互类型: "pickup", "place", "press", "grasp", "open", "close"
    confidence: float    # 置信度 [0.0, 1.0]
    approach_direction: np.ndarray  # (3,) 推荐的接近方向
    
    # 可选属性
    surface_material: Optional[str] = None  # 表面材质: "wood", "metal", "fabric", etc.
    stability_score: Optional[float] = None  # 稳定性评分 [0.0, 1.0]
    accessibility_score: Optional[float] = None  # 可达性评分 [0.0, 1.0]
    
    def __post_init__(self):
        """数据验证和标准化"""
        # 确保数组维度正确
        assert self.position.shape == (3,), f"position should be (3,), got {self.position.shape}"
        assert self.normal.shape == (3,), f"normal should be (3,), got {self.normal.shape}"
        assert self.approach_direction.shape == (3,), f"approach_direction should be (3,), got {self.approach_direction.shape}"
        
        # 标准化法向量和接近方向
        self.normal = self.normal / np.linalg.norm(self.normal)
        self.approach_direction = self.approach_direction / np.linalg.norm(self.approach_direction)
        
        # 验证置信度范围
        assert 0.0 <= self.confidence <= 1.0, f"confidence should be in [0,1], got {self.confidence}"
        
        # 验证交互类型
        valid_types = {"pickup", "place", "press", "grasp", "open", "close", "toggle"}
        assert self.interaction_type in valid_types, f"interaction_type should be one of {valid_types}"


@dataclass 
class RegionSignature:
    """
    物体特定区域的空间签名
    
    描述了物体的一个语义区域（如沙发的扶手、桌子的边缘等），
    包含该区域的几何特征和交互特性。
    """
    
    region_name: str  # 区域名称: "left_arm", "right_arm", "back", "seat", "top", "edge"
    point_indices: np.ndarray  # (N,) 属于该区域的点云索引
    center: np.ndarray  # (3,) 区域几何中心
    normal: np.ndarray  # (3,) 区域主法向量
    extent: np.ndarray  # (3,) 区域尺寸 [width, height, depth]
    
    # 交互特性评分 [0.0, 1.0]
    accessibility: float  # 可访问性：智能体能多容易接近这个区域
    stability: float     # 稳定性：在这个区域放置物体的稳定程度
    surface_quality: float  # 表面质量：表面的平整度和适合放置程度
    
    # 可选的几何特征
    bounding_box: Optional[np.ndarray] = None  # (2, 3) 区域边界框 [min_xyz, max_xyz]
    surface_area: Optional[float] = None  # 表面积
    volume: Optional[float] = None  # 体积
    
    # 可选的语义特征
    affordances: List[AffordancePoint] = field(default_factory=list)  # 该区域的交互点
    material_type: Optional[str] = None  # 材质类型
    texture_info: Optional[Dict[str, Any]] = None  # 纹理信息
    
    def __post_init__(self):
        """数据验证和标准化"""
        # 验证数组维度
        assert self.center.shape == (3,), f"center should be (3,), got {self.center.shape}"
        assert self.normal.shape == (3,), f"normal should be (3,), got {self.normal.shape}"
        assert self.extent.shape == (3,), f"extent should be (3,), got {self.extent.shape}"
        
        # 标准化法向量
        self.normal = self.normal / np.linalg.norm(self.normal)
        
        # 验证评分范围
        for score_name, score_value in [("accessibility", self.accessibility), 
                                       ("stability", self.stability),
                                       ("surface_quality", self.surface_quality)]:
            assert 0.0 <= score_value <= 1.0, f"{score_name} should be in [0,1], got {score_value}"
        
        # 验证区域名称格式
        valid_regions = {
            # 沙发区域
            "seat", "back", "left_arm", "right_arm", "cushion",
            # 桌子区域  
            "top", "left_edge", "right_edge", "front_edge", "back_edge", "corner",
            # 柜子区域
            "top_shelf", "middle_shelf", "bottom_shelf", "door", "handle",
            # 椅子区域
            "seat", "back", "left_armrest", "right_armrest", "legs",
            # 通用区域
            "surface", "edge", "side", "front", "back", "top", "bottom"
        }
        
        # 允许自定义区域名称，但给出警告
        if self.region_name not in valid_regions:
            print(f"⚠️ 自定义区域名称: '{self.region_name}' (不在标准区域列表中)")
    
    def get_interaction_points(self, interaction_type: str = None) -> List[AffordancePoint]:
        """获取指定类型的交互点"""
        if interaction_type is None:
            return self.affordances
        return [ap for ap in self.affordances if ap.interaction_type == interaction_type]
    
    def add_affordance_point(self, affordance: AffordancePoint):
        """添加交互点"""
        self.affordances.append(affordance)
    
    def compute_bounding_box(self, point_cloud: np.ndarray) -> np.ndarray:
        """根据点云计算边界框"""
        if len(self.point_indices) == 0:
            return np.array([[0, 0, 0], [0, 0, 0]])
        
        region_points = point_cloud[self.point_indices]
        min_coords = np.min(region_points, axis=0)
        max_coords = np.max(region_points, axis=0)
        
        self.bounding_box = np.array([min_coords, max_coords])
        return self.bounding_box


@dataclass
class SpatialSignature:
    """
    物体的完整空间签名
    
    包含物体的全部几何信息、语义区域、交互能力和空间关系，
    是精细化感知系统的核心数据结构。
    """
    
    # === 基础信息 ===
    object_id: str  # AI2THOR物体唯一ID
    object_type: str  # 物体类型: "Sofa", "DiningTable", "Chair", etc.
    bounding_box: Dict[str, Any]  # AI2THOR原始边界框信息
    
    # === 点云数据 ===
    point_cloud: np.ndarray  # (N, 3) 3D点云坐标
    point_colors: Optional[np.ndarray] = None  # (N, 3) RGB颜色 [0-255]
    point_normals: Optional[np.ndarray] = None  # (N, 3) 点法向量
    
    # === 6D位姿信息 ===
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))  # (3,) 物体中心位置
    orientation: np.ndarray = field(default_factory=lambda: np.eye(3))  # (3, 3) 旋转矩阵
    principal_axes: np.ndarray = field(default_factory=lambda: np.eye(3))  # (3, 3) 主成分方向
    scale: np.ndarray = field(default_factory=lambda: np.ones(3))  # (3,) 各轴向的尺度
    
    # === 语义区域 ===
    semantic_regions: Dict[str, RegionSignature] = field(default_factory=dict)
    # 例如: {"left_arm": RegionSignature, "right_arm": RegionSignature, "seat": RegionSignature}
    
    # === 交互能力 ===
    affordances: List[AffordancePoint] = field(default_factory=list)  # 全局交互点
    surface_normals: Optional[np.ndarray] = None  # (N, 3) 表面法向量场
    
    # === 空间关系 ===
    spatial_relations: Dict[str, Any] = field(default_factory=dict)  # 与其他物体的空间关系
    
    # === 元数据 ===
    confidence: float = 1.0  # 整体签名的置信度
    timestamp: Optional[float] = None  # 创建时间戳
    version: str = "1.0"  # 数据结构版本
    
    def __post_init__(self):
        """数据验证和完整性检查"""
        # 验证必要的数组维度
        if self.point_cloud.ndim != 2 or self.point_cloud.shape[1] != 3:
            raise ValueError(f"point_cloud should be (N, 3), got {self.point_cloud.shape}")
        
        n_points = self.point_cloud.shape[0]
        
        # 验证可选数组的维度
        if self.point_colors is not None:
            assert self.point_colors.shape == (n_points, 3), f"point_colors shape mismatch: expected {(n_points, 3)}, got {self.point_colors.shape}"
        
        if self.point_normals is not None:
            assert self.point_normals.shape == (n_points, 3), f"point_normals shape mismatch: expected {(n_points, 3)}, got {self.point_normals.shape}"
        
        # 验证6D位姿信息
        assert self.position.shape == (3,), f"position should be (3,), got {self.position.shape}"
        assert self.orientation.shape == (3, 3), f"orientation should be (3, 3), got {self.orientation.shape}"
        assert self.principal_axes.shape == (3, 3), f"principal_axes should be (3, 3), got {self.principal_axes.shape}"
        assert self.scale.shape == (3,), f"scale should be (3,), got {self.scale.shape}"
        
        # 验证旋转矩阵的正交性
        if not np.allclose(np.dot(self.orientation, self.orientation.T), np.eye(3), atol=1e-6):
            print("⚠️ 警告: orientation 不是正交矩阵，自动标准化")
            self.orientation = self._orthogonalize_matrix(self.orientation)
        
        # 验证置信度范围
        assert 0.0 <= self.confidence <= 1.0, f"confidence should be in [0,1], got {self.confidence}"
        
        # 设置时间戳
        if self.timestamp is None:
            import time
            self.timestamp = time.time()
    
    def _orthogonalize_matrix(self, matrix: np.ndarray) -> np.ndarray:
        """使用SVD正交化矩阵"""
        U, _, Vt = np.linalg.svd(matrix)
        return np.dot(U, Vt)
    
    def add_semantic_region(self, region: RegionSignature):
        """添加语义区域"""
        self.semantic_regions[region.region_name] = region
        print(f"✓ 添加语义区域: {region.region_name}")
    
    def get_region(self, region_name: str) -> Optional[RegionSignature]:
        """获取指定的语义区域"""
        return self.semantic_regions.get(region_name)
    
    def get_all_affordances(self, interaction_type: str = None) -> List[AffordancePoint]:
        """获取所有交互点（全局 + 区域）"""
        all_affordances = self.affordances.copy()
        
        for region in self.semantic_regions.values():
            all_affordances.extend(region.get_interaction_points(interaction_type))
        
        return all_affordances
    
    def get_surface_area(self) -> float:
        """估算物体表面积"""
        if len(self.point_cloud) == 0:
            return 0.0
        
        # 简单估算：使用边界框表面积
        bbox_min = np.min(self.point_cloud, axis=0)
        bbox_max = np.max(self.point_cloud, axis=0)
        dimensions = bbox_max - bbox_min
        
        # 计算长方体表面积
        w, h, d = dimensions
        surface_area = 2 * (w*h + w*d + h*d)
        
        return surface_area
    
    def get_volume(self) -> float:
        """估算物体体积"""
        if len(self.point_cloud) == 0:
            return 0.0
        
        # 简单估算：使用边界框体积
        bbox_min = np.min(self.point_cloud, axis=0)
        bbox_max = np.max(self.point_cloud, axis=0)
        dimensions = bbox_max - bbox_min
        
        return np.prod(dimensions)
    
    def transform_to_local_coordinates(self, world_points: np.ndarray) -> np.ndarray:
        """将世界坐标转换为物体局部坐标"""
        # 平移到物体中心
        centered_points = world_points - self.position
        
        # 旋转到物体坐标系
        local_points = np.dot(centered_points, self.orientation.T)
        
        # 按尺度缩放
        local_points = local_points / self.scale
        
        return local_points
    
    def transform_to_world_coordinates(self, local_points: np.ndarray) -> np.ndarray:
        """将物体局部坐标转换为世界坐标"""
        # 按尺度放大
        scaled_points = local_points * self.scale
        
        # 旋转到世界坐标系
        rotated_points = np.dot(scaled_points, self.orientation)
        
        # 平移到世界位置
        world_points = rotated_points + self.position
        
        return world_points
    
    def summary(self) -> Dict[str, Any]:
        """返回签名的摘要信息"""
        return {
            "object_id": self.object_id,
            "object_type": self.object_type,
            "n_points": len(self.point_cloud),
            "n_regions": len(self.semantic_regions),
            "n_affordances": len(self.get_all_affordances()),
            "surface_area": self.get_surface_area(),
            "volume": self.get_volume(),
            "confidence": self.confidence,
            "version": self.version
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        summary = self.summary()
        return (f"SpatialSignature({summary['object_type']}): "
                f"{summary['n_points']} points, "
                f"{summary['n_regions']} regions, "
                f"{summary['n_affordances']} affordances")


# =================== 工具函数 ===================

def create_simple_spatial_signature(object_id: str, 
                                   object_type: str,
                                   center_position: np.ndarray,
                                   points: np.ndarray) -> SpatialSignature:
    """
    创建简单的空间签名（用于测试和原型开发）
    
    Args:
        object_id: 物体ID
        object_type: 物体类型
        center_position: 中心位置
        points: 点云数据
    
    Returns:
        SpatialSignature对象
    """
    
    signature = SpatialSignature(
        object_id=object_id,
        object_type=object_type,
        bounding_box={},  # 简化版本
        point_cloud=points,
        position=center_position,
    )
    
    return signature


def merge_spatial_signatures(signatures: List[SpatialSignature]) -> SpatialSignature:
    """
    合并多个空间签名（用于组合物体）
    
    Args:
        signatures: 要合并的签名列表
    
    Returns:
        合并后的签名
    """
    if not signatures:
        raise ValueError("至少需要一个签名才能合并")
    
    if len(signatures) == 1:
        return signatures[0]
    
    # 合并点云
    all_points = np.vstack([sig.point_cloud for sig in signatures])
    
    # 计算整体中心
    center = np.mean(all_points, axis=0)
    
    # 创建合并的签名
    merged_id = "_".join([sig.object_id for sig in signatures])
    merged_type = "Composite"
    
    merged_signature = SpatialSignature(
        object_id=merged_id,
        object_type=merged_type,
        bounding_box={},
        point_cloud=all_points,
        position=center
    )
    
    # 合并语义区域
    for sig in signatures:
        for region_name, region in sig.semantic_regions.items():
            # 添加前缀避免冲突
            prefixed_name = f"{sig.object_id}_{region_name}"
            merged_signature.semantic_regions[prefixed_name] = region
    
    # 合并交互点
    for sig in signatures:
        merged_signature.affordances.extend(sig.affordances)
    
    return merged_signature 