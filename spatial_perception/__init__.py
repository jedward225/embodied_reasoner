"""
精细化感知模块 (Spatial Perception Module)

该模块实现了6D位姿估计、语义区域分割和精确交互点计算，
用于解决大型物体交互精度不足的问题。

核心组件:
- SpatialSignature: 物体空间签名
- RegionSignature: 区域空间签名  
- AffordancePoint: 交互点
- PointCloudReconstructor: 点云重建 (待实现)
- PoseEstimator: 6D位姿估计 (待实现)
- SemanticRegionSegmenter: 语义区域分割 (待实现)
"""

# 已实现的核心数据结构
from .data_structures import SpatialSignature, RegionSignature, AffordancePoint

# 待实现的模块 (第二周开始)
# from .point_cloud import PointCloudReconstructor
# from .pose_estimation import PoseEstimator
# from .semantic_segmentation import SemanticRegionSegmenter
# from .interaction_calculator import InteractionPointCalculator

__version__ = "0.1.0"
__author__ = "Embodied-Reasoner Team"

# 当前可用的类
__all__ = [
    "SpatialSignature",
    "RegionSignature", 
    "AffordancePoint",
    # "PointCloudReconstructor",      # 第二周实现
    # "PoseEstimator",                # 第二周实现  
    # "SemanticRegionSegmenter",      # 第三周实现
    # "InteractionPointCalculator"    # 第四周实现
] 