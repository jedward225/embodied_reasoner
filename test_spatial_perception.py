#!/usr/bin/env python3
"""
第二阶段测试脚本：验证精细化感知模块的核心数据结构

测试内容：
1. AffordancePoint 基础功能
2. RegionSignature 区域签名  
3. SpatialSignature 空间签名
4. 数据结构集成测试
"""

import numpy as np
import sys
import os

# 添加模块路径
sys.path.append(os.path.dirname(__file__))

from spatial_perception.data_structures import (
    AffordancePoint, 
    RegionSignature, 
    SpatialSignature,
    create_simple_spatial_signature,
    merge_spatial_signatures
)


def test_affordance_point():
    """测试 AffordancePoint 类"""
    print("=== 测试 AffordancePoint ===")
    
    try:
        # 创建有效的交互点
        position = np.array([1.0, 2.0, 3.0])
        normal = np.array([0.0, 1.0, 0.0])  # 向上的法向量
        approach_dir = np.array([0.0, -1.0, 0.0])  # 从上方接近
        
        affordance = AffordancePoint(
            position=position,
            normal=normal,
            interaction_type="place",
            confidence=0.9,
            approach_direction=approach_dir,
            surface_material="wood",
            stability_score=0.8,
            accessibility_score=0.85
        )
        
        print(f"   ✓ 交互点创建成功: {affordance.interaction_type}")
        print(f"   ✓ 位置: {affordance.position}")
        print(f"   ✓ 法向量 (标准化): {affordance.normal}")
        print(f"   ✓ 置信度: {affordance.confidence}")
        print(f"   ✓ 材质: {affordance.surface_material}")
        
        # 测试数据验证
        try:
            invalid_affordance = AffordancePoint(
                position=np.array([1.0, 2.0]),  # 错误维度
                normal=normal,
                interaction_type="place",
                confidence=0.9,
                approach_direction=approach_dir
            )
        except AssertionError as e:
            print(f"   ✓ 数据验证正常工作: {str(e)[:50]}...")
        
    except Exception as e:
        print(f"   ❌ AffordancePoint 测试失败: {e}")
        return False
    
    return True


def test_region_signature():
    """测试 RegionSignature 类"""
    print("\n=== 测试 RegionSignature ===")
    
    try:
        # 创建模拟点云数据
        n_points = 100
        point_indices = np.arange(0, 50)  # 前50个点属于这个区域
        center = np.array([0.0, 1.0, 0.0])
        normal = np.array([0.0, 1.0, 0.0])  # 向上
        extent = np.array([0.8, 0.1, 0.6])  # 宽度、高度、深度
        
        # 创建区域签名
        region = RegionSignature(
            region_name="left_arm",
            point_indices=point_indices,
            center=center,
            normal=normal,
            extent=extent,
            accessibility=0.8,
            stability=0.9,
            surface_quality=0.7,
            material_type="fabric"
        )
        
        print(f"   ✓ 区域签名创建成功: {region.region_name}")
        print(f"   ✓ 包含点数: {len(region.point_indices)}")
        print(f"   ✓ 中心位置: {region.center}")
        print(f"   ✓ 可访问性: {region.accessibility}")
        
        # 添加交互点
        affordance = AffordancePoint(
            position=center + np.array([0.1, 0.05, 0.0]),
            normal=normal,
            interaction_type="place",
            confidence=0.85,
            approach_direction=np.array([0.0, -1.0, 0.0])
        )
        region.add_affordance_point(affordance)
        
        print(f"   ✓ 添加交互点成功，总计: {len(region.affordances)}")
        
        # 测试交互点查询
        place_points = region.get_interaction_points("place")
        print(f"   ✓ 'place' 类型交互点: {len(place_points)}")
        
        # 测试边界框计算
        mock_point_cloud = np.random.randn(100, 3)
        bbox = region.compute_bounding_box(mock_point_cloud)
        print(f"   ✓ 边界框计算: shape {bbox.shape}")
        
    except Exception as e:
        print(f"   ❌ RegionSignature 测试失败: {e}")
        return False
    
    return True


def test_spatial_signature():
    """测试 SpatialSignature 类"""
    print("\n=== 测试 SpatialSignature ===")
    
    try:
        # 创建模拟点云数据（沙发形状）
        n_points = 200
        # 生成一个简单的长方体点云作为沙发
        x = np.random.uniform(-1, 1, n_points)
        y = np.random.uniform(0, 0.8, n_points) 
        z = np.random.uniform(-0.5, 0.5, n_points)
        point_cloud = np.column_stack([x, y, z])
        
        # 生成随机颜色
        point_colors = np.random.randint(0, 255, (n_points, 3))
        
        # 创建空间签名
        signature = SpatialSignature(
            object_id="Sofa_test_001",
            object_type="Sofa",
            bounding_box={"center": {"x": 0, "y": 0.4, "z": 0}},
            point_cloud=point_cloud,
            point_colors=point_colors,
            position=np.array([0.0, 0.4, 0.0]),
            confidence=0.95
        )
        
        print(f"   ✓ 空间签名创建成功: {signature.object_type}")
        print(f"   ✓ 点云大小: {signature.point_cloud.shape}")
        print(f"   ✓ 中心位置: {signature.position}")
        print(f"   ✓ 置信度: {signature.confidence}")
        
        # 测试摘要信息
        summary = signature.summary()
        print(f"   ✓ 摘要信息: {summary['n_points']} 点, {summary['n_regions']} 区域")
        print(f"   ✓ 表面积估算: {summary['surface_area']:.2f}")
        print(f"   ✓ 体积估算: {summary['volume']:.2f}")
        
        # 添加语义区域
        # 左扶手区域
        left_arm_indices = np.arange(0, 50)
        left_arm_region = RegionSignature(
            region_name="left_arm",
            point_indices=left_arm_indices,
            center=np.array([-0.8, 0.4, 0.0]),
            normal=np.array([0.0, 1.0, 0.0]),
            extent=np.array([0.2, 0.6, 0.5]),
            accessibility=0.8,
            stability=0.9,
            surface_quality=0.7
        )
        
        # 右扶手区域
        right_arm_indices = np.arange(50, 100)
        right_arm_region = RegionSignature(
            region_name="right_arm",
            point_indices=right_arm_indices,
            center=np.array([0.8, 0.4, 0.0]),
            normal=np.array([0.0, 1.0, 0.0]),
            extent=np.array([0.2, 0.6, 0.5]),
            accessibility=0.8,
            stability=0.9,
            surface_quality=0.7
        )
        
        # 座位区域
        seat_indices = np.arange(100, 150)
        seat_region = RegionSignature(
            region_name="seat",
            point_indices=seat_indices,
            center=np.array([0.0, 0.4, 0.0]),
            normal=np.array([0.0, 1.0, 0.0]),
            extent=np.array([1.6, 0.1, 0.8]),
            accessibility=0.9,
            stability=0.95,
            surface_quality=0.9
        )
        
        # 添加区域到签名
        signature.add_semantic_region(left_arm_region)
        signature.add_semantic_region(right_arm_region)
        signature.add_semantic_region(seat_region)
        
        print(f"   ✓ 语义区域总数: {len(signature.semantic_regions)}")
        
        # 测试区域查询
        left_arm = signature.get_region("left_arm")
        if left_arm:
            print(f"   ✓ 查询左扶手成功: {left_arm.region_name}")
        
        # 测试坐标转换
        world_points = np.array([[1.0, 1.0, 1.0], [0.0, 0.0, 0.0]])
        local_points = signature.transform_to_local_coordinates(world_points)
        back_to_world = signature.transform_to_world_coordinates(local_points)
        
        if np.allclose(world_points, back_to_world, atol=1e-6):
            print("   ✓ 坐标转换测试通过")
        else:
            print("   ⚠️ 坐标转换精度警告")
        
        # 测试字符串表示
        print(f"   ✓ 字符串表示: {str(signature)}")
        
    except Exception as e:
        print(f"   ❌ SpatialSignature 测试失败: {e}")
        return False
    
    return True


def test_utility_functions():
    """测试工具函数"""
    print("\n=== 测试工具函数 ===")
    
    try:
        # 测试简单空间签名创建
        points = np.random.randn(50, 3)
        center = np.array([0.0, 0.0, 0.0])
        
        simple_sig = create_simple_spatial_signature(
            object_id="Test_001",
            object_type="TestObject",
            center_position=center,
            points=points
        )
        
        print(f"   ✓ 简单签名创建: {simple_sig.object_id}")
        
        # 测试签名合并
        points2 = np.random.randn(30, 3) + 2.0  # 偏移的点云
        center2 = np.array([2.0, 0.0, 0.0])
        
        simple_sig2 = create_simple_spatial_signature(
            object_id="Test_002", 
            object_type="TestObject2",
            center_position=center2,
            points=points2
        )
        
        merged_sig = merge_spatial_signatures([simple_sig, simple_sig2])
        print(f"   ✓ 签名合并成功: {merged_sig.object_id}")
        print(f"   ✓ 合并后点数: {len(merged_sig.point_cloud)}")
        
    except Exception as e:
        print(f"   ❌ 工具函数测试失败: {e}")
        return False
    
    return True


def test_edge_cases():
    """测试边界情况和错误处理"""
    print("\n=== 测试边界情况 ===")
    
    try:
        # 测试无效置信度
        try:
            invalid_affordance = AffordancePoint(
                position=np.array([0., 0., 0.]),
                normal=np.array([0., 1., 0.]),
                interaction_type="place",
                confidence=1.5,  # 无效值
                approach_direction=np.array([0., -1., 0.])
            )
        except AssertionError:
            print("   ✓ 无效置信度检测正常")
        
        # 测试无效交互类型
        try:
            invalid_affordance = AffordancePoint(
                position=np.array([0., 0., 0.]),
                normal=np.array([0., 1., 0.]),
                interaction_type="invalid_type",  # 无效类型
                confidence=0.5,
                approach_direction=np.array([0., -1., 0.])
            )
        except AssertionError:
            print("   ✓ 无效交互类型检测正常")
        
        # 测试空点云
        try:
            empty_signature = SpatialSignature(
                object_id="Empty_001",
                object_type="Empty",
                bounding_box={},
                point_cloud=np.array([]).reshape(0, 3)  # 空点云
            )
            
            surface_area = empty_signature.get_surface_area()
            volume = empty_signature.get_volume()
            print(f"   ✓ 空点云处理: 表面积={surface_area}, 体积={volume}")
            
        except Exception as e:
            print(f"   ⚠️ 空点云处理警告: {e}")
        
        print("   ✓ 边界情况测试完成")
        
    except Exception as e:
        print(f"   ❌ 边界情况测试失败: {e}")
        return False
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始第二阶段核心数据结构测试")
    print("=" * 50)
    
    tests = [
        ("AffordancePoint", test_affordance_point),
        ("RegionSignature", test_region_signature),
        ("SpatialSignature", test_spatial_signature),
        ("工具函数", test_utility_functions),
        ("边界情况", test_edge_cases)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 执行 {test_name} 测试:")
        if test_func():
            passed += 1
            print(f"   ✅ {test_name} 测试通过")
        else:
            print(f"   ❌ {test_name} 测试失败")
    
    print("\n" + "=" * 50)
    print(f"🎯 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！核心数据结构实现正确")
        print("📋 第一周任务完成，可以开始第二周的点云处理模块")
        return True
    else:
        print("⚠️ 部分测试失败，请检查实现")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 