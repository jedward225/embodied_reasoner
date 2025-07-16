#!/usr/bin/env python3
"""Simple test to debug the evaluation issue."""

import sys
import os
import traceback

# Test basic imports
try:
    from ai2thor_engine.RocAgent import RocAgent
    print("✅ RocAgent imported")
except Exception as e:
    print(f"❌ RocAgent import failed: {e}")

try:
    from ai2thor.controller import Controller
    from ai2thor.platform import CloudRendering
    print("✅ AI2THOR imported")
except Exception as e:
    print(f"❌ AI2THOR import failed: {e}")

# Test controller creation
try:
    print("🎮 Creating controller...")
    controller = Controller(
        platform=CloudRendering,
        scene='FloorPlan1',
        headless=True,
        width=800,
        height=450,
        snapToGrid=False,
        quality='Medium',
        agentMode="default",
        massThreshold=None,
        visibilityDistance=20,
        gridSize=0.1,
        renderDepthImage=False,
        renderInstanceSegmentation=False,
        fieldOfView=90
    )
    print("✅ Controller created")
    
    # Test basic action
    event = controller.step(dict(action='Pass'))
    print(f"✅ Basic action success: {event.metadata['lastActionSuccess']}")
    print(f"🔍 Event frame: {event.frame is not None}")
    print(f"🔍 Event frame type: {type(event.frame)}")
    if event.frame is not None:
        print(f"🔍 Frame shape: {event.frame.shape}")
    else:
        print("❌ Frame is None - this is the problem!")
    
    # Test agent creation
    print("🤖 Creating RocAgent...")
    
    # Load test data
    import json
    with open('../data/test_mini.json') as f:
        test_data = json.load(f)[0]
    
    print(f"📄 Test data: {test_data}")
    
    # Create agent
    save_path = f"./data/simple_test/{test_data['identity']}_{test_data['tasktype']}_{test_data['scene']}_{test_data['instruction_idx']}"
    print(f"💾 Save path: {save_path}")
    
    agent = RocAgent(
        controller, 
        save_path, 
        test_data['scene'], 
        visibilityDistance=20, 
        gridSize=0.1, 
        fieldOfView=90,
        target_objects=test_data["target_objects"],
        related_objects=test_data["related_objects"],
        navigable_objects=test_data["navigable_objects"],
        taskid=test_data["identity"],
        platform_type="GPU"
    )
    
    print("✅ RocAgent created successfully")
    
    # Test basic functionality
    print("🔍 Testing agent functionality...")
    
    # Get objects
    objects = agent.eventobject.get_objects_type(agent.controller.last_event)
    print(f"✅ Found {len(objects)} object types")
    
    # Test action execution
    print("⚡ Testing action execution...")
    success, image_fp, legal_locations, legal_objects = agent.exec("init", None)
    print(f"✅ Init action: success={success}, image={image_fp is not None}")
    
    controller.stop()
    print("✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    traceback.print_exc()
    if 'controller' in locals():
        try:
            controller.stop()
        except:
            pass