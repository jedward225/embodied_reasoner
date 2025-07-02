"""
6D位姿估计模块

该模块基于主成分分析(PCA)估计物体的6D位姿，包括3D位置和3D旋转。
主要用于为SpatialSignature提供准确的物体姿态信息。

核心功能：
- 基于点云的PCA分析
- 6D位姿计算 (position + orientation)
- 主成分方向估计
- 尺度因子计算
"""

import numpy as np
from typing import Tuple, Optional, Dict
from sklearn.decomposition import PCA
from scipy.spatial.transform import Rotation
import warnings

from .data_structures import SpatialSignature


class PoseEstimator:
    """
    基于点云的6D位姿估计器
    
    使用主成分分析(PCA)来估计物体的主要方向和位置，
    适用于具有明显几何结构的物体。
    """
    
    def __init__(self, min_points: int = 10, center_method: str = "mean"):
        """
        初始化位姿估计器
        
        Args:
            min_points: 最少点数要求
            center_method: 中心点计算方法 ("mean", "median", "geometric_median")
        """
        self.min_points = min_points
        self.center_method = center_method
        
        # PCA相关参数
        self.pca_explained_variance_threshold = 0.01  # 主成分解释方差阈值
        self.orientation_consistency_threshold = 0.8   # 方向一致性阈值
        
    def compute_center(self, points: np.ndarray) -> np.ndarray:
        """
        计算点云中心
        
        Args:
            points: 点云 (N, 3)
            
        Returns:
            中心点坐标 (3,)
        """
        if len(points) == 0:
            return np.zeros(3)
        
        if self.center_method == "mean":
            return np.mean(points, axis=0)
        elif self.center_method == "median":
            return np.median(points, axis=0)
        elif self.center_method == "geometric_median":
            # 几何中位数：对异常值更鲁棒
            return self._compute_geometric_median(points)
        else:
            raise ValueError(f"不支持的中心计算方法: {self.center_method}")
    
    def _compute_geometric_median(self, points: np.ndarray, max_iter: int = 100, tol: float = 1e-6) -> np.ndarray:
        """
        计算几何中位数（Weiszfeld算法）
        
        Args:
            points: 点云 (N, 3)
            max_iter: 最大迭代次数
            tol: 收敛容差
            
        Returns:
            几何中位数 (3,)
        """
        if len(points) == 1:
            return points[0]
        
        # 初始化为算术平均值
        median = np.mean(points, axis=0)
        
        for i in range(max_iter):
            # 计算距离
            distances = np.linalg.norm(points - median, axis=1)
            
            # 避免除零
            distances = np.maximum(distances, 1e-8)
            
            # 权重为距离的倒数
            weights = 1.0 / distances
            weights = weights / np.sum(weights)
            
            # 更新中位数
            new_median = np.sum(points * weights.reshape(-1, 1), axis=0)
            
            # 检查收敛
            if np.linalg.norm(new_median - median) < tol:
                break
                
            median = new_median
        
        return median
    
    def compute_pca(self, points: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        计算点云的主成分分析
        
        Args:
            points: 中心化后的点云 (N, 3)
            
        Returns:
            Tuple[主成分方向(3,3), 特征值(3,), 解释方差比(3,)]
        """
        if len(points) < 3:
            # 点太少，返回单位矩阵
            return np.eye(3), np.ones(3), np.ones(3) / 3
        
        # 使用PCA分析
        pca = PCA(n_components=3)
        pca.fit(points)
        
        # 获取主成分方向（按特征值大小排序）
        components = pca.components_  # (3, 3)
        eigenvalues = pca.explained_variance_  # (3,)
        explained_variance_ratio = pca.explained_variance_ratio_  # (3,)
        
        return components, eigenvalues, explained_variance_ratio
    
    def align_principal_axes(self, components: np.ndarray, points: np.ndarray) -> np.ndarray:
        """
        调整主成分方向，使其符合常见的物体方向约定
        
        Args:
            components: PCA主成分 (3, 3)
            points: 中心化后的点云 (N, 3)
            
        Returns:
            调整后的主成分方向 (3, 3)
        """
        aligned_components = components.copy()
        
        # 确保右手坐标系
        if np.linalg.det(aligned_components) < 0:
            aligned_components[2] = -aligned_components[2]
        
        # 对于每个主成分，选择更合理的方向
        for i in range(3):
            axis = aligned_components[i]
            
            # 投影点云到该轴
            projections = np.dot(points, axis)
            
            # 如果大部分点在负方向，翻转轴
            if np.mean(projections) < 0:
                aligned_components[i] = -axis
        
        return aligned_components
    
    def estimate_scale(self, points: np.ndarray, principal_axes: np.ndarray) -> np.ndarray:
        """
        估计物体在各主成分方向上的尺度
        
        Args:
            points: 中心化后的点云 (N, 3)
            principal_axes: 主成分方向 (3, 3)
            
        Returns:
            各轴向的尺度 (3,)
        """
        if len(points) == 0:
            return np.ones(3)
        
        # 将点云投影到主成分坐标系
        projected_points = np.dot(points, principal_axes.T)
        
        # 计算各轴向的范围
        min_coords = np.min(projected_points, axis=0)
        max_coords = np.max(projected_points, axis=0)
        scales = max_coords - min_coords
        
        # 避免零尺度
        scales = np.maximum(scales, 1e-6)
        
        return scales
    
    def validate_pose_estimation(self, 
                                position: np.ndarray,
                                orientation: np.ndarray,
                                explained_variance: np.ndarray,
                                n_points: int) -> Tuple[float, Dict[str, float]]:
        """
        验证位姿估计的质量
        
        Args:
            position: 估计的位置 (3,)
            orientation: 估计的旋转矩阵 (3, 3)
            explained_variance: PCA解释方差比 (3,)
            n_points: 点云点数
            
        Returns:
            Tuple[整体置信度, 详细评分]
        """
        scores = {}
        
        # 1. 点数充足性评分
        scores["point_sufficiency"] = min(1.0, n_points / 100.0)
        
        # 2. PCA解释方差评分
        # 主成分应该能解释大部分方差
        scores["pca_quality"] = np.sum(explained_variance[:2])  # 前两个主成分
        
        # 3. 方向一致性评分
        # 检查旋转矩阵的正交性
        orthogonality_error = np.linalg.norm(
            np.dot(orientation, orientation.T) - np.eye(3)
        )
        scores["orthogonality"] = max(0.0, 1.0 - orthogonality_error * 10)
        
        # 4. 方差分布评分
        # 好的估计应该有明显的主方向
        variance_ratio = explained_variance[0] / (explained_variance[1] + 1e-8)
        scores["direction_clarity"] = min(1.0, variance_ratio / 3.0)
        
        # 5. 数值稳定性评分
        position_norm = np.linalg.norm(position)
        scores["numerical_stability"] = 1.0 if position_norm < 100 else 0.5
        
        # 计算整体置信度（加权平均）
        weights = {
            "point_sufficiency": 0.2,
            "pca_quality": 0.3,
            "orthogonality": 0.2,
            "direction_clarity": 0.2,
            "numerical_stability": 0.1
        }
        
        confidence = sum(scores[key] * weights[key] for key in weights.keys())
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence, scores
    
    def estimate_6d_pose(self, point_cloud: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, Dict]:
        """
        估计点云的6D位姿
        
        Args:
            point_cloud: 输入点云 (N, 3) 或 (N, 6) [x,y,z] 或 [x,y,z,r,g,b]
            
        Returns:
            Tuple[
                position(3,): 3D位置,
                orientation(3,3): 3D旋转矩阵,
                principal_axes(3,3): 主成分方向,
                scale(3,): 各轴向尺度,
                confidence(float): 置信度,
                metadata(dict): 详细信息
            ]
        """
        metadata = {
            "n_points": len(point_cloud),
            "success": False,
            "error_message": None,
            "pca_info": {},
            "validation_scores": {}
        }
        
        try:
            # 提取3D坐标
            if point_cloud.shape[1] >= 3:
                points_3d = point_cloud[:, :3]
            else:
                raise ValueError(f"点云维度不足: {point_cloud.shape}")
            
            # 检查点数
            if len(points_3d) < self.min_points:
                metadata["error_message"] = f"点数不足: {len(points_3d)} < {self.min_points}"
                return np.zeros(3), np.eye(3), np.eye(3), np.ones(3), 0.0, metadata
            
            # 1. 计算中心位置
            position = self.compute_center(points_3d)
            
            # 2. 中心化点云
            centered_points = points_3d - position
            
            # 3. PCA分析
            components, eigenvalues, explained_variance = self.compute_pca(centered_points)
            
            metadata["pca_info"] = {
                "eigenvalues": eigenvalues.tolist(),
                "explained_variance_ratio": explained_variance.tolist(),
                "total_explained_variance": float(np.sum(explained_variance))
            }
            
            # 4. 调整主成分方向
            aligned_components = self.align_principal_axes(components, centered_points)
            
            # 5. 计算旋转矩阵（转置得到世界坐标系到物体坐标系的转换）
            orientation = aligned_components.T
            
            # 6. 计算尺度
            scale = self.estimate_scale(centered_points, aligned_components)
            
            # 7. 验证估计质量
            confidence, validation_scores = self.validate_pose_estimation(
                position, orientation, explained_variance, len(points_3d)
            )
            
            metadata["validation_scores"] = validation_scores
            metadata["success"] = True
            
            return position, orientation, aligned_components, scale, confidence, metadata
            
        except Exception as e:
            metadata["error_message"] = str(e)
            return np.zeros(3), np.eye(3), np.eye(3), np.ones(3), 0.0, metadata
    
    def estimate_pose_for_object_type(self, 
                                     point_cloud: np.ndarray,
                                     object_type: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, Dict]:
        """
        针对特定物体类型的位姿估计
        
        Args:
            point_cloud: 点云数据
            object_type: 物体类型 ("Sofa", "Chair", "Table", etc.)
            
        Returns:
            同 estimate_6d_pose
        """
        # 根据物体类型调整参数
        original_method = self.center_method
        
        try:
            if object_type.lower() in ["sofa", "couch"]:
                # 沙发通常较大，使用几何中位数更鲁棒
                self.center_method = "geometric_median"
            elif object_type.lower() in ["chair", "stool"]:
                # 椅子结构相对规整，使用均值即可
                self.center_method = "mean"
            elif object_type.lower() in ["table", "desk", "diningtable"]:
                # 桌子通常有平整表面，使用均值
                self.center_method = "mean"
            
            # 执行位姿估计
            result = self.estimate_6d_pose(point_cloud)
            
            # 在metadata中添加物体类型信息
            position, orientation, principal_axes, scale, confidence, metadata = result
            metadata["object_type"] = object_type
            metadata["adapted_center_method"] = self.center_method
            
            return position, orientation, principal_axes, scale, confidence, metadata
            
        finally:
            # 恢复原始参数
            self.center_method = original_method
    
    def create_spatial_signature_from_pose(self,
                                         object_id: str,
                                         object_type: str,
                                         point_cloud: np.ndarray,
                                         ai2thor_bounding_box: Dict) -> SpatialSignature:
        """
        从位姿估计结果创建SpatialSignature
        
        Args:
            object_id: 物体ID
            object_type: 物体类型
            point_cloud: 点云数据 (N, 6) [x,y,z,r,g,b]
            ai2thor_bounding_box: AI2THOR边界框信息
            
        Returns:
            SpatialSignature对象
        """
        # 估计6D位姿
        position, orientation, principal_axes, scale, confidence, metadata = \
            self.estimate_pose_for_object_type(point_cloud, object_type)
        
        # 分离坐标和颜色
        points_3d = point_cloud[:, :3] if point_cloud.shape[1] >= 3 else point_cloud
        colors = point_cloud[:, 3:6] if point_cloud.shape[1] >= 6 else None
        
        # 创建空间签名
        signature = SpatialSignature(
            object_id=object_id,
            object_type=object_type,
            bounding_box=ai2thor_bounding_box,
            point_cloud=points_3d,
            point_colors=colors,
            position=position,
            orientation=orientation,
            principal_axes=principal_axes,
            scale=scale,
            confidence=confidence
        )
        
        # 添加位姿估计的元数据
        signature.spatial_relations["pose_estimation"] = metadata
        
        return signature


# =================== 工具函数 ===================

def compare_pose_estimates(pose1: Tuple, pose2: Tuple) -> Dict[str, float]:
    """
    比较两个位姿估计的差异
    
    Args:
        pose1, pose2: 位姿估计结果 (position, orientation, ...)
        
    Returns:
        差异分析结果
    """
    pos1, ori1 = pose1[0], pose1[1]
    pos2, ori2 = pose2[0], pose2[1]
    
    # 位置差异
    position_diff = np.linalg.norm(pos1 - pos2)
    
    # 旋转差异（使用旋转角度）
    rotation_diff_matrix = np.dot(ori1, ori2.T)
    rotation_angle = np.arccos(np.clip((np.trace(rotation_diff_matrix) - 1) / 2, -1, 1))
    rotation_diff_degrees = np.degrees(rotation_angle)
    
    return {
        "position_difference": float(position_diff),
        "rotation_difference_degrees": float(rotation_diff_degrees),
        "confidence_diff": float(pose1[4] - pose2[4]) if len(pose1) > 4 and len(pose2) > 4 else 0.0
    }


def visualize_pose_estimation(signature: SpatialSignature) -> Dict[str, str]:
    """
    生成位姿估计的可视化描述
    
    Args:
        signature: 空间签名
        
    Returns:
        可视化描述
    """
    description = {
        "summary": f"{signature.object_type} 位姿估计",
        "position": f"位置: ({signature.position[0]:.2f}, {signature.position[1]:.2f}, {signature.position[2]:.2f})",
        "scale": f"尺度: {signature.scale[0]:.2f} x {signature.scale[1]:.2f} x {signature.scale[2]:.2f}",
        "confidence": f"置信度: {signature.confidence:.2f}",
        "principal_directions": "主方向: " + ", ".join([
            f"轴{i+1}: ({signature.principal_axes[i, 0]:.2f}, {signature.principal_axes[i, 1]:.2f}, {signature.principal_axes[i, 2]:.2f})"
            for i in range(3)
        ])
    }
    
    return description 