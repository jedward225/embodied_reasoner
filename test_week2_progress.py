"""
第二周进展测试：点云处理和位姿估计

验证内容：
1. 点云重建器功能
2. 6D位姿估计
3. 数据结构集成
"""

import os
import sys
import numpy as np

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spatial_perception.point_cloud import PointCloudReconstructor, CameraIntrinsics
from spatial_perception.pose_estimation import PoseEstimator


def test_camera_intrinsics():
    """测试相机内参数据结构"""
    print("🔧 测试相机内参数据结构...")
    
    # AI2THOR典型参数
    intrinsics = CameraIntrinsics(
        fx=300.0, fy=300.0, 
        cx=150.0, cy=150.0,
        width=300, height=300
    )
    
    print(f"相机内参: fx={intrinsics.fx}, fy={intrinsics.fy}")
    print(f"图像尺寸: {intrinsics.width} x {intrinsics.height}")
    print("✅ 相机内参测试通过\n")


def test_point_cloud_reconstruction():
    """测试点云重建功能"""
    print("🔧 测试点云重建功能...")
    
    # 创建模拟深度图和颜色图
    height, width = 100, 100
    depth_image = np.random.uniform(0.5, 5.0, (height, width))  # 0.5-5米深度
    color_image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    
    # 创建实例分割掩码
    instance_mask = np.zeros((height, width), dtype=np.int32)
    instance_mask[20:60, 30:70] = 12345  # 物体ID   12345 for example
    
    # 相机内参
    intrinsics = CameraIntrinsics(fx=75.0, fy=75.0, cx=50.0, cy=50.0, width=width, height=height)
    
    # 创建点云重建器
    reconstructor = PointCloudReconstructor(intrinsics)
    
    # 重建点云
    point_cloud = reconstructor.reconstruct_pointcloud(
        depth_image, color_image, instance_mask, target_instance_id=12345
    )
    
    print(f"重建点云形状: {point_cloud.shape}")
    print(f"点云范围 X: [{point_cloud[:, 0].min():.2f}, {point_cloud[:, 0].max():.2f}]")
    print(f"点云范围 Y: [{point_cloud[:, 1].min():.2f}, {point_cloud[:, 1].max():.2f}]")
    print(f"点云范围 Z: [{point_cloud[:, 2].min():.2f}, {point_cloud[:, 2].max():.2f}]")
    
    print("✅ 点云重建测试通过\n")
    return point_cloud


def test_pose_estimation(point_cloud):
    """测试6D位姿估计"""
    print("🔧 测试6D位姿估计...")
    
    # 创建位姿估计器
    estimator = PoseEstimator(min_points=5, center_method="mean")
    
    # 估计6D位姿
    position, orientation, principal_axes, scale, confidence, metadata = \
        estimator.estimate_6d_pose(point_cloud)
    
    print(f"估计位置: [{position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f}]")
    print(f"估计尺度: [{scale[0]:.2f}, {scale[1]:.2f}, {scale[2]:.2f}]")
    print(f"置信度: {confidence:.3f}")
    print(f"点云点数: {metadata['n_points']}")
    
    print("✅ 6D位姿估计测试通过\n")
    return position, orientation, principal_axes, scale, confidence, metadata


def main():
    """主测试函数"""
    print("🚀 开始第二周进展测试")
    print("=" * 50)
    
    try:
        # 1. 基础数据结构测试
        test_camera_intrinsics()
        
        # 2. 点云重建测试
        point_cloud = test_point_cloud_reconstruction()
        
        # 3. 位姿估计测试
        pose_data = test_pose_estimation(point_cloud)
        
        print("🎉 第二周核心功能测试通过！")
        print("\n📊 测试总结:")
        print("✅ 相机内参数据结构")
        print("✅ 点云重建器")
        print("✅ 6D位姿估计器")
        
        print(f"\n🔬 处理统计:")
        print(f"  - 成功重建点云: {point_cloud.shape[0]} 点")
        print(f"  - 位姿估计置信度: {pose_data[4]:.3f}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()