#!/usr/bin/env python3

import sys
sys.path.append('evaluate')

from ai2thor.controller import Controller
from ai2thor.platform import CloudRendering
from collections import defaultdict
import json

def explore_scene_objects(scene_name="FloorPlan1"):
    """Explore objects in a scene to find multiple objects of same type."""
    
    controller = Controller(
        platform=CloudRendering,
        snapToGrid=False,
        quality='Medium',
        agentMode="default",
        massThreshold=None,
        scene=scene_name,
        visibilityDistance=20,
        gridSize=0.1,
        renderDepthImage=False,
        renderInstanceSegmentation=False,
        width=800,
        height=450,
        fieldOfView=90,
    )
    
    # Get all objects in scene
    event = controller.step(dict(action='Pass'))
    objects = event.metadata['objects']
    
    # Group objects by type
    object_types = defaultdict(list)
    for obj in objects:
        object_types[obj['objectType']].append(obj)
    
    print(f"=== Objects in {scene_name} ===")
    print(f"Total objects: {len(objects)}")
    print("\nObjects with multiple instances:")
    
    disambiguation_candidates = []
    
    for obj_type, obj_list in object_types.items():
        if len(obj_list) > 1:
            print(f"\n{obj_type}: {len(obj_list)} instances")
            for i, obj in enumerate(obj_list):
                pos = obj['position']
                print(f"  {i+1}. {obj['objectId']} at ({pos['x']:.2f}, {pos['y']:.2f}, {pos['z']:.2f})")
                if obj.get('visible', False):
                    print(f"     Visible: {obj['visible']}")
                if obj.get('pickupable', False):
                    print(f"     Pickupable: {obj['pickupable']}")
            
            # Good candidates for disambiguation testing
            if len(obj_list) >= 2 and any(obj.get('pickupable', False) for obj in obj_list):
                disambiguation_candidates.append(obj_type)
    
    print(f"\n=== Good candidates for disambiguation testing ===")
    for candidate in disambiguation_candidates:
        print(f"- {candidate}")
    
    controller.stop()
    return disambiguation_candidates

if __name__ == "__main__":
    candidates = explore_scene_objects("FloorPlan1")
    
    if candidates:
        print(f"\nFound {len(candidates)} object types with multiple instances for testing!")
    else:
        print("\nNo multiple objects found in FloorPlan1. Let's try other scenes...")
        
        # Try other FloorPlans
        for scene_num in [2, 3, 4, 5]:
            scene_name = f"FloorPlan{scene_num}"
            print(f"\n=== Trying {scene_name} ===")
            try:
                candidates = explore_scene_objects(scene_name)
                if candidates:
                    print(f"Found candidates in {scene_name}!")
                    break
            except Exception as e:
                print(f"Error with {scene_name}: {e}")