"""
点云重建模块

该模块负责从AI2THOR提供的深度图、RGB图和实例分割掩码中重建3D点云，
为后续的6D位姿估计和语义区域分割提供基础数据。

主要功能：
- 深度图到点云的转换
- 相机内参处理
- 实例分割掩码应用
- 点云颜色信息附加
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
import cv2
from dataclasses import dataclass


@dataclass
class CameraIntrinsics:
    """相机内参数据结构"""
    fx: float  # 焦距 x
    fy: float  # 焦距 y  
    cx: float  # 主点 x
    cy: float  # 主点 y
    width: int  # 图像宽度
    height: int  # 图像高度
    
    def to_matrix(self) -> np.ndarray:
        """转换为3x3内参矩阵"""
        return np.array([
            [self.fx, 0, self.cx],
            [0, self.fy, self.cy],
            [0, 0, 1]
        ])


class PointCloudReconstructor:
    """
    从AI2THOR深度图重建点云
    
    该类提供了完整的点云重建流程，包括：
    1. 深度图预处理
    2. 3D点云重建
    3. 颜色信息附加
    4. 实例分割掩码应用
    """
    
    def __init__(self, camera_intrinsics: Optional[CameraIntrinsics] = None):
        """
        初始化点云重建器
        
        Args:
            camera_intrinsics: 相机内参，如果为None则使用AI2THOR默认参数
        """
        self.camera_intrinsics = camera_intrinsics
        self.depth_scale = 1000.0  # AI2THOR深度图的缩放因子
        
    def get_ai2thor_default_intrinsics(self, width: int = 800, height: int = 450, fov: float = 90.0) -> CameraIntrinsics:
        """
        获取AI2THOR的默认相机内参
        
        Args:
            width: 图像宽度
            height: 图像高度
            fov: 视野角度（度）
            
        Returns:
            CameraIntrinsics对象
        """
        # 根据FOV计算焦距
        fov_rad = np.radians(fov)
        fx = fy = (width / 2.0) / np.tan(fov_rad / 2.0)
        
        # 主点通常在图像中心
        cx = width / 2.0
        cy = height / 2.0
        
        return CameraIntrinsics(
            fx=fx, fy=fy, cx=cx, cy=cy,
            width=width, height=height
        )
    
    def preprocess_depth_image(self, depth_image: np.ndarray) -> np.ndarray:
        """
        预处理深度图
        
        Args:
            depth_image: 原始深度图 (H, W)
            
        Returns:
            处理后的深度图，单位为米
        """
        # AI2THOR的深度图通常已经是以米为单位
        # 处理无效深度值（通常为0或极大值）
        processed_depth = depth_image.copy().astype(np.float32)
        
        # 过滤异常值
        processed_depth[processed_depth <= 0] = np.nan
        processed_depth[processed_depth > 20.0] = np.nan  # 超过20米的深度值视为无效
        
        # 可选：进行深度图平滑
        if np.any(~np.isnan(processed_depth)):
            # 使用中值滤波去除噪声
            processed_depth = cv2.medianBlur(processed_depth, 3)
        
        return processed_depth
    
    def depth_to_pointcloud(self, 
                           depth_image: np.ndarray,
                           camera_intrinsics: Optional[CameraIntrinsics] = None) -> np.ndarray:
        """
        将深度图转换为3D点云
        
        Args:
            depth_image: 深度图 (H, W)，单位为米
            camera_intrinsics: 相机内参，如果为None则使用默认值
            
        Returns:
            点云数组 (N, 3)，坐标为 [x, y, z]
        """
        if camera_intrinsics is None:
            height, width = depth_image.shape
            camera_intrinsics = self.get_ai2thor_default_intrinsics(width, height)
        
        height, width = depth_image.shape
        
        # 生成像素坐标网格
        u, v = np.meshgrid(np.arange(width), np.arange(height))
        
        # 展平为1D数组
        u_flat = u.flatten()
        v_flat = v.flatten()
        depth_flat = depth_image.flatten()
        
        # 过滤有效深度值
        valid_mask = ~np.isnan(depth_flat) & (depth_flat > 0)
        u_valid = u_flat[valid_mask]
        v_valid = v_flat[valid_mask]
        depth_valid = depth_flat[valid_mask]
        
        if len(depth_valid) == 0:
            # 如果没有有效深度值，返回空点云
            return np.empty((0, 3))
        
        # 像素坐标转相机坐标
        # x = (u - cx) * z / fx
        # y = (v - cy) * z / fy  
        # z = depth
        x = (u_valid - camera_intrinsics.cx) * depth_valid / camera_intrinsics.fx
        y = (v_valid - camera_intrinsics.cy) * depth_valid / camera_intrinsics.fy
        z = depth_valid
        
        # AI2THOR坐标系转换：y轴向上，z轴向前
        # 相机坐标系：x右，y下，z前 -> 世界坐标系：x右，y上，z前
        points_3d = np.column_stack([x, -y, z])  # 翻转y轴
        
        return points_3d
    
    def attach_colors(self, 
                     points_3d: np.ndarray,
                     rgb_image: np.ndarray,
                     depth_image: np.ndarray,
                     camera_intrinsics: Optional[CameraIntrinsics] = None) -> np.ndarray:
        """
        为点云附加颜色信息
        
        Args:
            points_3d: 3D点云 (N, 3)
            rgb_image: RGB图像 (H, W, 3)
            depth_image: 深度图 (H, W)
            camera_intrinsics: 相机内参
            
        Returns:
            带颜色的点云 (N, 6) [x, y, z, r, g, b]
        """
        if camera_intrinsics is None:
            height, width = depth_image.shape
            camera_intrinsics = self.get_ai2thor_default_intrinsics(width, height)
        
        if len(points_3d) == 0:
            return np.empty((0, 6))
        
        # 3D点投影回像素坐标
        x, y, z = points_3d[:, 0], -points_3d[:, 1], points_3d[:, 2]  # 恢复相机坐标系
        
        u = (x * camera_intrinsics.fx / z + camera_intrinsics.cx).astype(int)
        v = (y * camera_intrinsics.fy / z + camera_intrinsics.cy).astype(int)
        
        # 确保像素坐标在图像范围内
        height, width = rgb_image.shape[:2]
        valid_mask = (u >= 0) & (u < width) & (v >= 0) & (v < height)
        
        # 提取颜色
        colors = np.zeros((len(points_3d), 3), dtype=np.uint8)
        if np.any(valid_mask):
            u_valid = u[valid_mask]
            v_valid = v[valid_mask]
            colors[valid_mask] = rgb_image[v_valid, u_valid]
        
        # 合并坐标和颜色
        colored_points = np.column_stack([points_3d, colors])
        
        return colored_points
    
    def apply_instance_mask(self,
                           colored_points: np.ndarray,
                           instance_mask: np.ndarray,
                           target_instance_id: int,
                           depth_image: np.ndarray,
                           camera_intrinsics: Optional[CameraIntrinsics] = None) -> np.ndarray:
        """
        应用实例分割掩码，提取特定物体的点云
        
        Args:
            colored_points: 带颜色的点云 (N, 6)
            instance_mask: 实例分割掩码 (H, W)
            target_instance_id: 目标实例ID
            depth_image: 深度图 (H, W)
            camera_intrinsics: 相机内参
            
        Returns:
            目标物体的点云 (M, 6)，M <= N
        """
        if camera_intrinsics is None:
            height, width = depth_image.shape
            camera_intrinsics = self.get_ai2thor_default_intrinsics(width, height)
        
        if len(colored_points) == 0:
            return np.empty((0, 6))
        
        # 3D点投影回像素坐标以查找对应的实例ID
        points_3d = colored_points[:, :3]
        x, y, z = points_3d[:, 0], -points_3d[:, 1], points_3d[:, 2]
        
        u = (x * camera_intrinsics.fx / z + camera_intrinsics.cx).astype(int)
        v = (y * camera_intrinsics.fy / z + camera_intrinsics.cy).astype(int)
        
        # 确保像素坐标在图像范围内
        height, width = instance_mask.shape
        valid_mask = (u >= 0) & (u < width) & (v >= 0) & (v < height)
        
        # 检查对应像素的实例ID
        instance_mask_values = np.zeros(len(colored_points), dtype=instance_mask.dtype)
        if np.any(valid_mask):
            u_valid = u[valid_mask]
            v_valid = v[valid_mask]
            instance_mask_values[valid_mask] = instance_mask[v_valid, u_valid]
        
        # 提取目标实例的点
        target_mask = instance_mask_values == target_instance_id
        target_points = colored_points[target_mask]
        
        return target_points
    
    def reconstruct_pointcloud(self, 
                              depth_image: np.ndarray,
                              rgb_image: np.ndarray, 
                              instance_mask: Optional[np.ndarray] = None,
                              target_instance_id: Optional[int] = None,
                              camera_intrinsics: Optional[CameraIntrinsics] = None) -> np.ndarray:
        """
        完整的点云重建流程
        
        Args:
            depth_image: 深度图 (H, W)
            rgb_image: RGB图像 (H, W, 3)
            instance_mask: 实例分割掩码 (H, W)，可选
            target_instance_id: 目标实例ID，可选
            camera_intrinsics: 相机内参，可选
            
        Returns:
            重建的点云 (N, 6) [x, y, z, r, g, b]
        """
        # 1. 预处理深度图
        processed_depth = self.preprocess_depth_image(depth_image)
        
        # 2. 深度图转点云
        points_3d = self.depth_to_pointcloud(processed_depth, camera_intrinsics)
        
        if len(points_3d) == 0:
            return np.empty((0, 6))
        
        # 3. 附加颜色信息
        colored_points = self.attach_colors(points_3d, rgb_image, processed_depth, camera_intrinsics)
        
        # 4. 应用实例掩码（如果提供）
        if instance_mask is not None and target_instance_id is not None:
            colored_points = self.apply_instance_mask(
                colored_points, instance_mask, target_instance_id, 
                processed_depth, camera_intrinsics
            )
        
        return colored_points
    
    def get_object_pointcloud_from_ai2thor_event(self, 
                                                event,
                                                object_id: str,
                                                enable_depth: bool = True,
                                                enable_instance_segmentation: bool = True) -> Tuple[np.ndarray, Dict]:
        """
        从AI2THOR事件中提取特定物体的点云
        
        Args:
            event: AI2THOR事件对象
            object_id: 目标物体ID
            enable_depth: 是否启用深度图
            enable_instance_segmentation: 是否启用实例分割
            
        Returns:
            Tuple[点云数据, 元数据信息]
        """
        # 获取图像数据
        rgb_image = event.frame  # (H, W, 3)
        
        metadata = {
            "object_id": object_id,
            "scene": event.metadata.get("sceneName", "Unknown"),
            "camera_position": event.metadata["cameraPosition"],
            "camera_rotation": event.metadata["agent"]["rotation"],
            "success": False,
            "error_message": None
        }
        
        try:
            # 获取深度图
            if enable_depth and hasattr(event, 'depth_frame') and event.depth_frame is not None:
                depth_image = event.depth_frame
            else:
                metadata["error_message"] = "深度图不可用"
                return np.empty((0, 6)), metadata
            
            # 获取实例分割掩码
            instance_mask = None
            target_instance_id = None
            
            if enable_instance_segmentation and hasattr(event, 'instance_segmentation_frame'):
                instance_mask = event.instance_segmentation_frame
                
                # 查找目标物体的实例ID
                for obj in event.metadata["objects"]:
                    if obj["objectId"] == object_id:
                        # AI2THOR中，实例ID通常存储在color_to_object_id映射中
                        if hasattr(event, 'color_to_object_id'):
                            for color, obj_id in event.color_to_object_id.items():
                                if obj_id == object_id:
                                    # 颜色值转换为实例ID
                                    target_instance_id = color
                                    break
                        break
                
                if target_instance_id is None:
                    metadata["error_message"] = f"未找到物体 {object_id} 的实例ID"
                    # 仍然可以重建整个场景的点云，只是不过滤特定物体
            
            # 重建点云
            colored_points = self.reconstruct_pointcloud(
                depth_image=depth_image,
                rgb_image=rgb_image,
                instance_mask=instance_mask,
                target_instance_id=target_instance_id
            )
            
            metadata["success"] = True
            metadata["n_points"] = len(colored_points)
            
            return colored_points, metadata
            
        except Exception as e:
            metadata["error_message"] = str(e)
            return np.empty((0, 6)), metadata


# =================== 工具函数 ===================

def save_pointcloud_to_ply(points: np.ndarray, filename: str):
    """
    将点云保存为PLY格式文件
    
    Args:
        points: 点云数据 (N, 6) [x, y, z, r, g, b]
        filename: 输出文件名
    """
    if len(points) == 0:
        print("警告: 点云为空，无法保存")
        return
    
    header = f"""ply
format ascii 1.0
element vertex {len(points)}
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
"""
    
    with open(filename, 'w') as f:
        f.write(header)
        for point in points:
            x, y, z, r, g, b = point
            f.write(f"{x:.6f} {y:.6f} {z:.6f} {int(r)} {int(g)} {int(b)}\n")
    
    print(f"点云已保存到: {filename}")


def visualize_pointcloud_stats(points: np.ndarray) -> Dict:
    """
    分析点云统计信息
    
    Args:
        points: 点云数据 (N, 6) [x, y, z, r, g, b]
        
    Returns:
        统计信息字典
    """
    if len(points) == 0:
        return {"n_points": 0, "error": "空点云"}
    
    xyz = points[:, :3]
    rgb = points[:, 3:6]
    
    stats = {
        "n_points": len(points),
        "spatial_extent": {
            "x_range": [float(np.min(xyz[:, 0])), float(np.max(xyz[:, 0]))],
            "y_range": [float(np.min(xyz[:, 1])), float(np.max(xyz[:, 1]))],
            "z_range": [float(np.min(xyz[:, 2])), float(np.max(xyz[:, 2]))],
        },
        "center": [float(np.mean(xyz[:, 0])), float(np.mean(xyz[:, 1])), float(np.mean(xyz[:, 2]))],
        "color_stats": {
            "mean_rgb": [float(np.mean(rgb[:, 0])), float(np.mean(rgb[:, 1])), float(np.mean(rgb[:, 2]))],
            "std_rgb": [float(np.std(rgb[:, 0])), float(np.std(rgb[:, 1])), float(np.std(rgb[:, 2]))]
        }
    }
    
    return stats 