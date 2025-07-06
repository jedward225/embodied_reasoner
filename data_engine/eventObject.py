import ai2thor.server
from typing import List, Dict, Tuple
import re
from typing import Optional

class EventObject:
    def __init__(self, event: ai2thor.server.Event):
        self.objects = event.metadata["objects"]
        self.object2color = event.object_id_to_color
        self.color2object = event.color_to_object_id
        _, enhanced_mapping = self.get_objects()
        
        # 新的映射方式 (推荐使用)
        self.id2object = enhanced_mapping["by_id"]        # objectId -> object
        self.type2objects = enhanced_mapping["by_type"]   # objectType -> [objects]
        
        # 保持向后兼容性 (但会有同名物体覆盖警告)
        self.item2object = enhanced_mapping["by_name"]    # name -> object (兼容性)  


    def get_objects(self) -> Tuple[List[dict], Dict[str, dict]]:
        id2objects = {}  # objectId -> object mapping (唯一映射)
        type2objects = {}  # objectType -> [objects] mapping (类型到实例列表)
        
        for item in self.objects:
            # 使用唯一ID作为主映射键，解决同名物体混淆问题
            id2objects[item["objectId"]] = item
            
            # 维护类型到实例列表的映射，支持按类型查找
            if item["objectType"] not in type2objects:
                type2objects[item["objectType"]] = []
            type2objects[item["objectType"]].append(item)
        
        # 为了兼容性，也保留旧的name映射（但会有覆盖问题的警告）
        name2object = {}
        for item in self.objects:
            if item["name"] in name2object:
                print(f"⚠️ Warning: Duplicate object name '{item['name']}' detected. It is recommended to use objectId for precise access.")
            name2object[item["name"]] = item
            
        enhanced_mapping = {
            "by_id": id2objects,      # 推荐使用：按唯一ID映射
            "by_type": type2objects,   # 新增：按类型映射到实例列表  
            "by_name": name2object     # 兼容性：按名称映射（可能覆盖）
        }
        
        return self.objects, enhanced_mapping    
    
    def get_all_item_position(self) -> dict:
        item2position = {}
        for item in self.objects:
            item2position[item["name"]] = item["position"]
        return item2position     

    def get_visible_objects(self) -> Tuple[List[dict],List[dict]]:
        return [obj['name'] for obj in self.objects if obj["visible"]], [obj for obj in self.objects if obj["visible"]]

    def get_isInteractable_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["isInteractable"]]

    def get_receptacle_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["receptacle"]]

    def get_toggleable_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["toggleable"]]

    def get_breakable_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["breakable"]]

    def get_isToggled_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["isToggled"]]

    def get_isBroken_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["isBroken"]]

    def get_canFillWithLiquid_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["canFillWithLiquid"]]

    def get_isFilledWithLiquid_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["isFilledWithLiquid"]]

    def get_fillLiquid_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["fillLiquid"]]

    def get_dirtyable_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["dirtyable"]]

    def get_isDirty_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["isDirty"]]

    def get_canBeUsedUp_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["canBeUsedUp"]]

    def get_isUsedUp_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["isUsedUp"]]

    def get_cookable_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["cookable"]]

    def get_isCooked_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["isCooked"]]

    def get_isHeatSource_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["isHeatSource"]]

    def get_isColdSource_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["isColdSource"]]

    def get_sliceable_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["sliceable"]]

    def get_openable_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["openable"]]

    def get_isOpen_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["isOpen"]]

    def get_pickupable_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["pickupable"]]

    def get_isPickedUp_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["isPickedUp"]]

    def get_moveable_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["moveable"]]
    
    def get_isMoving_objects(self, ) -> List[dict]:
        return [obj for obj in self.objects if obj["isMoving"]]
    
    def get_object_color(self, object_id: str) -> str:
        return self.object2color[object_id]
    
    def get_color_object(self, color: str):
        return self.color2object[color]

    def get_item_mass(self, item_name: str) -> float:
        return self.item2object[item_name]["mass"]
    
    def get_item_volume(self, item_name: str) -> float:
        item_size = self.item2object[item_name]["axisAlignedBoundingBox"]["size"]
        # 保留四位小数
        return round(item_size["x"] * item_size["y"] * item_size["z"], 4)
    
    # 获取物品平面面积
    def get_item_surface_area(self, item_name: str) -> float:
        item_size = self.item2object[item_name]["axisAlignedBoundingBox"]["size"]
        x = item_size["x"]
        y = item_size["y"]
        z = item_size["z"]
        max_surface= max(x*y, x*z, y*z)
        # 保留四位小数
        return round(max_surface, 4)
    
    def get_item_position(self, item_name: str) -> dict:
        return self.item2object[item_name]["position"]
    
    def get_item_orientation(self, item_name: str) -> dict:
        return self.item2object[item_name]["rotation"]
    
    def get_object_by_id(self, object_id: str) -> Optional[dict]:
        """根据唯一objectId获取物体信息（推荐使用）"""
        return self.id2object.get(object_id, None)
    
    def get_objects_by_type(self, object_type: str) -> List[dict]:
        """根据物体类型获取所有同类物体列表"""
        return self.type2objects.get(object_type, [])
    
    def find_object_id_by_name(self, name_pattern: str) -> List[str]:
        """根据名称模式查找匹配的objectId列表"""
        matching_ids = []
        for object_id, obj in self.id2object.items():
            if name_pattern.lower() in obj["name"].lower():
                matching_ids.append(object_id)
        return matching_ids


def extract_item(response):
    # Extract the item from the response
    # text = "Some text [[Television_deb5e431]] and other text [[SideTable_cbdfb67a]]."
    matches = re.findall(r'\[\[(.*?)\]\]', response)
    if matches:
        last_match = matches[-1]
    else:
        print("No matches found.")
    return last_match

def match_object(instruction, mapping_dict):
    """
    根据指令匹配物体，支持新的映射格式
    mapping_dict: 可以是旧格式的 item2object 或新格式的 enhanced_mapping
    """
    # 兼容新旧两种格式
    if isinstance(mapping_dict, dict) and "by_id" in mapping_dict:
        # 新格式：enhanced_mapping
        item2object = mapping_dict["by_name"]  # 使用name映射作为兼容
        id2object = mapping_dict["by_id"]      # 可用于精确访问
    else:
        # 旧格式：直接的 item2object 字典
        item2object = mapping_dict
        id2object = mapping_dict
    
    # response = call_llm(instruction, str(list(item2object.keys())))
    # item = extract_item(response)
    # return item2object[item]
    
    # item2object['TissueBox_88aca81e']
    # item2object['Television_deb5e431']
    # 'DiningTable_806ce8fd'
    # CoffeeTable_d8cc0ea5
    # Sofa_9b5cac5c
    # 'Ottoman_89afd8ca'
    
    # 尝试按objectId访问（推荐方式）
    if 'LightSwitch_c3c009ea' in id2object:
        return id2object['LightSwitch_c3c009ea']
    
    # 回退到name访问（兼容性）
    for name, obj in item2object.items():
        if 'LightSwitch' in name:
            return obj
            
    return None
# item2object['Newspaper_a1a8109a']
'''
Previous code:
def match_object(instruction, item2object):
    # response = call_llm(instruction, str(list(item2object.keys())))
    # item = extract_item(response)
    # return item2object[item]
    # item2object['TissueBox_88aca81e']
    # item2object['Television_deb5e431']
    # 'DiningTable_806ce8fd'
    # CoffeeTable_d8cc0ea5
    # Sofa_9b5cac5c
    # 'Ottoman_89afd8ca'
    return item2object['LightSwitch_c3c009ea']
# item2object['Newspaper_a1a8109a']

This function is not used in the later code. So here is fine...
'''