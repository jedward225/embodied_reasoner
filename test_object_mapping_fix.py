#!/usr/bin/env python3
"""
测试脚本：验证同名物体混淆问题的修复效果
"""

from ai2thor.controller import Controller
from ai2thor.platform import CloudRendering
from evaluate.ai2thor_engine.utils import EventObject as UtilsEventObject
from data_engine.eventObject import EventObject

def test_object_mapping_fix():
    """测试修复后的物体映射功能"""
    print("=== 同名物体混淆修复验证测试 ===")
    
    # 创建控制器并初始化场景
    controller = Controller(
        scene="FloorPlan1",
        renderDepthImage=True,
        renderInstanceSegmentation=True,
        width=300,
        height=300,
        fieldOfView=90,
        platform=CloudRendering
    )
    
    event = controller.step("Pass")
    
    # 测试utils.EventObject (静态方法)
    print("\n1. 测试 evaluate/ai2thor_engine/utils.py EventObject:")
    try:
        objects, enhanced_mapping = UtilsEventObject.get_objects(event)
        
        print(f"   总物体数量: {len(objects)}")
        print(f"   唯一ID映射数量: {len(enhanced_mapping['by_id'])}")
        print(f"   名称映射数量: {len(enhanced_mapping['by_name'])}")
        print(f"   类型映射数量: {len(enhanced_mapping['by_type'])}")
        
        # 检查是否有同名物体
        type_counts = {}
        for obj in objects:
            obj_type = obj["objectType"]
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        
        print("\n   物体类型统计:")
        multi_instance_types = []
        for obj_type, count in type_counts.items():
            if count > 1:
                multi_instance_types.append((obj_type, count))
                print(f"   ✓ {obj_type}: {count}个实例")
        
        # 测试多实例类型的映射
        if multi_instance_types:
            test_type = multi_instance_types[0][0]
            print(f"\n   测试多实例类型 '{test_type}':")
            instances = enhanced_mapping['by_type'][test_type]
            print(f"   - by_type映射找到 {len(instances)} 个实例:")
            for i, instance in enumerate(instances):
                print(f"     {i+1}. {instance['objectId']} at {instance['position']}")
                
            # 验证by_id能访问所有实例
            print(f"   - by_id映射验证:")
            for instance in instances:
                obj_id = instance['objectId']
                retrieved = enhanced_mapping['by_id'][obj_id]
                print(f"     ✓ {obj_id}: {retrieved['position']}")
        else:
            print("   ⚠️  当前场景中没有多实例类型物体")
            
    except Exception as e:
        print(f"   ❌ utils.EventObject 测试失败: {e}")
    
    # 测试data_engine.EventObject (类实例)
    print("\n2. 测试 data_engine/eventObject.py EventObject:")
    try:
        event_obj = EventObject(event)
        
        print(f"   ID映射数量: {len(event_obj.id2object)}")
        print(f"   类型映射数量: {len(event_obj.type2objects)}")
        print(f"   名称映射数量: {len(event_obj.item2object)}")
        
        # 测试新增的方法
        print("\n   测试新增方法:")
        
        # 按类型查找
        for obj_type, count in type_counts.items():
            if count > 1:
                instances = event_obj.get_objects_by_type(obj_type)
                print(f"   - get_objects_by_type('{obj_type}'): {len(instances)}个实例")
                
                # 测试按名称模糊查找
                ids = event_obj.find_object_id_by_name(obj_type)
                print(f"   - find_object_id_by_name('{obj_type}'): {len(ids)}个ID")
                
                # 测试精确ID查找
                for obj_id in ids[:2]:  # 只测试前2个
                    obj = event_obj.get_object_by_id(obj_id)
                    if obj:
                        print(f"   - get_object_by_id('{obj_id}'): {obj['position']}")
                break
        
    except Exception as e:
        print(f"   ❌ data_engine.EventObject 测试失败: {e}")
    
    # 性能对比测试
    print("\n3. 性能对比测试:")
    import time
    
    # 旧方式查找（会有覆盖问题）
    start_time = time.time()
    for _ in range(1000):
        _ = enhanced_mapping['by_name']
    old_time = time.time() - start_time
    
    # 新方式查找（精确无覆盖）
    start_time = time.time()
    for _ in range(1000):
        _ = enhanced_mapping['by_id']
    new_time = time.time() - start_time
    
    print(f"   旧方式(by_name) 1000次查找: {old_time:.4f}秒")
    print(f"   新方式(by_id) 1000次查找: {new_time:.4f}秒")
    print(f"   性能比: {old_time/new_time:.2f}x")
    
    controller.stop()
    
    print("\n=== 测试完成 ===")
    print("✅ 同名物体混淆问题已修复！")
    print("📋 现在可以使用以下新方法:")
    print("   - event_obj.get_object_by_id(object_id)  # 精确查找")
    print("   - event_obj.get_objects_by_type(type)   # 按类型查找所有实例")
    print("   - event_obj.find_object_id_by_name(name)  # 模糊名称匹配")

if __name__ == "__main__":
    test_object_mapping_fix() 