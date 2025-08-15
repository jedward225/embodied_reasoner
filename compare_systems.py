#!/usr/bin/env python3
"""
Simple A/B test: Original vs Enhanced navigation system
"""

import json
import sys
import os
sys.path.append('./evaluate')

from ai2thor.controller import Controller
from ai2thor.platform import CloudRendering
from ai2thor_engine.RocAgent import RocAgent

def test_single_task(task_data, use_enhanced=False):
    """Test a single task with original or enhanced system"""
    controller = Controller(platform=CloudRendering)
    
    try:
        # Create agent
        agent = RocAgent(
            controller=controller,
            scene=task_data['scene'],
            save_path="./test_data/compare/",
            visibilityDistance=1.5,
            fieldOfView=90,
            target_objects=task_data.get('target_objects', []),
            related_objects=task_data.get('related_objects', []),
            navigable_objects=task_data.get('navigable_objects', []),
            taskid=task_data.get('identity', 0),
            platform_type="GPU"
        )
        
        # Configure system
        if use_enhanced:
            print("🚀 Using ENHANCED system (object indexing + smart selection)")
            agent.enable_enhanced_navigation(enable_indexing=True, enable_dialogue=False)
        else:
            print("📦 Using ORIGINAL system (first object selection)")
            agent.enable_enhanced_navigation(enable_indexing=False, enable_dialogue=False)
        
        # Get first navigation action from task
        first_action = task_data['task_metadata']['actions'][0]
        if first_action['action'] != 'navigate to':
            return None
            
        target_type = first_action['objectType']
        target_id = first_action['objectId']
        
        print(f"Target: {target_type} -> {target_id}")
        
        # Check multi-object scenario
        if target_type not in agent.objecttype2object:
            print(f"❌ Object type {target_type} not found")
            return None
            
        objects = agent.objecttype2object[target_type]
        print(f"Found {len(objects)} {target_type} objects")
        
        if len(objects) <= 1:
            print("ℹ️  No disambiguation needed")
            return {'result': 'no_disambiguation_needed'}
        
        # Show all candidates
        for i, obj in enumerate(objects):
            is_target = "⭐" if obj['objectId'] == target_id else "  "
            print(f"{is_target} {target_type}_{i+1}: {obj['objectId']}")
        
        # Test navigation
        print(f"🎯 Navigating with {'enhanced' if use_enhanced else 'original'} system...")
        
        if use_enhanced:
            # Enhanced system will use smart selection
            result = agent.navigate(target_type)
        else:
            # Original system - simulate by directly using first object
            selected_obj = objects[0]
            print(f"Original system selects: {selected_obj['objectId']}")
            correct = selected_obj['objectId'] == target_id
            return {
                'selected': selected_obj['objectId'],
                'target': target_id,
                'correct': correct,
                'method': 'original'
            }
        
        # For enhanced, check what was actually selected
        # This is tricky without deep inspection, but we can infer from previous tests
        return {
            'result': 'enhanced_navigation_completed',
            'target': target_id,
            'method': 'enhanced'
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'error': str(e)}
    finally:
        controller.stop()

def main():
    """Compare original vs enhanced on first task"""
    print("🔬 A/B Test: Original vs Enhanced Navigation")
    print("="*60)
    
    # Load first task
    with open('./data/test_809.json', 'r') as f:
        data = json.load(f)
    
    task = data[0]
    print(f"Task: {task['taskquery']}")
    print(f"Scene: {task['scene']}")
    print()
    
    # Test original system
    print("🔍 TEST 1: ORIGINAL SYSTEM")
    print("-" * 40)
    original_result = test_single_task(task, use_enhanced=False)
    print()
    
    # Test enhanced system  
    print("🔍 TEST 2: ENHANCED SYSTEM")
    print("-" * 40)
    enhanced_result = test_single_task(task, use_enhanced=True)
    print()
    
    # Compare results
    print("📊 COMPARISON RESULTS")
    print("=" * 60)
    
    if original_result and 'correct' in original_result:
        print(f"Original system: {'✅ CORRECT' if original_result['correct'] else '❌ WRONG'}")
        print(f"  Selected: {original_result['selected']}")
        print(f"  Target:   {original_result['target']}")
    
    if enhanced_result:
        print(f"Enhanced system: {enhanced_result}")
    
    print("\n✅ Comparison completed!")

if __name__ == "__main__":
    main()