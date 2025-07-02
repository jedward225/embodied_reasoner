#!/usr/bin/env python3
"""
AI2THOR 环境测试脚本
根据 Arrangement.md 第一阶段的要求，验证 AI2THOR 能否正常工作
"""

from ai2thor.controller import Controller
from ai2thor.platform import CloudRendering
import os
import time

def test_ai2thor_basic():
    """基础 AI2THOR 功能测试"""
    print("=== AI2THOR 基础功能测试 ===")
    
    try:
        # 创建控制器
        print("1. 创建 AI2THOR Controller...")
        controller = Controller(
            scene="FloorPlan1",
            renderDepthImage=True,
            renderInstanceSegmentation=True,
            width=300,
            height=300,
            fieldOfView=90,
            platform=CloudRendering
        )
        print("✓ Controller 创建成功")
        
        # 获取初始状态
        print("2. 获取初始状态...")
        event = controller.step("Pass")
        print(f"✓ Agent位置: {event.metadata['agent']['position']}")
        print(f"✓ 场景: {event.metadata['sceneName']}")
        
        # 测试深度图获取
        print("3. 测试深度图获取...")
        if hasattr(event, 'depth_frame') and event.depth_frame is not None:
            print(f"✓ 深度图尺寸: {event.depth_frame.shape}")
        else:
            print("⚠ 深度图获取失败")
            
        # 测试实例分割掩码
        print("4. 测试实例分割掩码...")
        if hasattr(event, 'instance_masks') and event.instance_masks:
            print(f"✓ 实例掩码数量: {len(event.instance_masks)}")
        else:
            print("⚠ 实例掩码获取失败")
            
        # 测试物体列表
        print("5. 测试物体列表...")
        objects = event.metadata['objects']
        visible_objects = [obj for obj in objects if obj['visible']]
        print(f"✓ 场景中物体总数: {len(objects)}")
        print(f"✓ 可见物体数量: {len(visible_objects)}")
        
        # 显示前5个可见物体
        print("前5个可见物体:")
        for i, obj in enumerate(visible_objects[:5]):
            print(f"  - {obj['objectType']}: {obj['objectId']}")
            
        # 测试基础移动
        print("6. 测试基础移动...")
        move_event = controller.step("MoveAhead")
        if move_event.metadata['lastActionSuccess']:
            print("✓ 前进移动成功")
            new_pos = move_event.metadata['agent']['position']
            print(f"✓ 新位置: {new_pos}")
        else:
            print("⚠ 移动失败")
            
        # 测试旋转
        print("7. 测试旋转...")
        rotate_event = controller.step("RotateRight")
        if rotate_event.metadata['lastActionSuccess']:
            print("✓ 右转成功")
            new_rotation = rotate_event.metadata['agent']['rotation']
            print(f"✓ 新旋转角度: {new_rotation}")
        else:
            print("⚠ 旋转失败")
        
        # 清理
        controller.stop()
        print("✓ Controller 已关闭")
        
        return True
        
    except Exception as e:
        print(f"❌ AI2THOR 测试失败: {e}")
        return False

def test_camera_intrinsics():
    """测试相机内参获取"""
    print("\n=== 相机内参测试 ===")
    
    try:
        controller = Controller(
            scene="FloorPlan1",
            renderDepthImage=True,
            width=800,
            height=450,
            fieldOfView=90
        )
        
        event = controller.step("Pass")
        
        # 获取相机内参
        if 'cameraClippingPlanes' in event.metadata:
            clipping = event.metadata['cameraClippingPlanes']
            print(f"✓ 相机裁剪平面: {clipping}")
            
        # 计算焦距（基于FOV）
        import math
        fov_rad = math.radians(90)  # FOV in radians
        width, height = 800, 450
        fx = width / (2 * math.tan(fov_rad / 2))
        fy = fx  # 假设方形像素
        cx, cy = width / 2, height / 2
        
        print(f"✓ 计算的内参矩阵:")
        print(f"  fx = {fx:.2f}, fy = {fy:.2f}")
        print(f"  cx = {cx:.2f}, cy = {cy:.2f}")
        
        controller.stop()
        return True
        
    except Exception as e:
        print(f"❌ 相机内参测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始 AI2THOR 环境验证...")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 基础功能测试
    basic_success = test_ai2thor_basic()
    
    # 相机内参测试
    camera_success = test_camera_intrinsics()
    
    # 总结
    print("\n=== 测试结果总结 ===")
    print(f"基础功能测试: {'✓ 通过' if basic_success else '❌ 失败'}")
    print(f"相机内参测试: {'✓ 通过' if camera_success else '❌ 失败'}")
    
    if basic_success and camera_success:
        print("\n🎉 AI2THOR 环境验证成功！")
        print("可以继续进行后续开发工作。")
    else:
        print("\n⚠ 某些测试失败，请检查 AI2THOR 安装。")
    
    return basic_success and camera_success

if __name__ == "__main__":
    main() 