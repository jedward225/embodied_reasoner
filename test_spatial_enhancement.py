#!/usr/bin/env python3
"""
Comprehensive test script for spatial enhancement integration.
Handles server issues and provides multiple testing approaches.
"""

import sys
import os
import time
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/home/jiajunliu/embodied_reasoner')

def test_module_imports():
    """Test that all spatial enhancement modules can be imported."""
    print("🔍 Testing module imports...")
    
    try:
        from spatial_enhancement.enhanced_agent import EnhancedRocAgent
        from spatial_enhancement.spatial_calculator import SpatialRelationCalculator
        from spatial_enhancement.geometric_analyzer import GeometricAnalyzer
        from spatial_enhancement.heuristic_detector import HeuristicAmbiguityDetector
        print("✅ All spatial enhancement modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_evaluate_integration():
    """Test the evaluate module integration."""
    print("\n🔍 Testing evaluate module integration...")
    
    try:
        from evaluate.ai2thor_engine.EnhancedRocAgent import EnhancedRocAgent
        print("✅ EnhancedRocAgent imported from evaluate module")
        return True
    except ImportError as e:
        print(f"❌ Evaluate integration error: {e}")
        return False

def test_spatial_calculator_standalone():
    """Test spatial calculator without AI2-THOR controller."""
    print("\n🔍 Testing spatial calculator standalone...")
    
    try:
        from spatial_enhancement.spatial_calculator import SpatialRelationCalculator
        
        # Mock objects for testing
        mock_objects = [
            {
                'objectId': 'Book_1',
                'objectType': 'Book',
                'position': {'x': 1.0, 'y': 0.5, 'z': 2.0},
                'visible': True
            },
            {
                'objectId': 'Book_2', 
                'objectType': 'Book',
                'position': {'x': -1.0, 'y': 0.5, 'z': 2.0},
                'visible': True
            },
            {
                'objectId': 'Book_3',
                'objectType': 'Book', 
                'position': {'x': 0.0, 'y': 0.5, 'z': 4.0},
                'visible': True
            }
        ]
        
        # Mock agent position
        agent_position = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        
        # Create calculator
        calculator = SpatialRelationCalculator()
        
        # Test relation calculation
        relations = calculator.calculate_relative_positions(mock_objects, agent_position)
        print(f"✅ Calculated relations for {len(relations)} objects")
        
        # Test spatial constraint extraction
        constraints = calculator.extract_spatial_constraints("拿起左边的书")
        print(f"✅ Extracted spatial constraints: {constraints}")
        
        # Test spatial matching
        best_match, confidence = calculator.find_best_spatial_match(mock_objects, "拿起左边的书")
        print(f"✅ Best spatial match: {best_match} (confidence: {confidence:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Spatial calculator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_geometric_analyzer_standalone():
    """Test geometric analyzer without AI2-THOR controller."""
    print("\n🔍 Testing geometric analyzer standalone...")
    
    try:
        from spatial_enhancement.geometric_analyzer import GeometricAnalyzer
        
        # Mock object with AABB data
        mock_object = {
            'objectId': 'Sofa_1',
            'objectType': 'Sofa',
            'axisAlignedBoundingBox': {
                'center': {'x': 0.0, 'y': 0.5, 'z': 2.0},
                'size': {'x': 2.0, 'y': 1.0, 'z': 1.0}
            },
            'position': {'x': 0.0, 'y': 0.0, 'z': 2.0}
        }
        
        # Create analyzer
        analyzer = GeometricAnalyzer()
        
        # Test observation strategy analysis
        strategy = analyzer.analyze_observation_requirements(mock_object)
        print(f"✅ Observation strategy: {strategy.strategy_type}")
        print(f"   - Distance: {strategy.optimal_distance:.2f}m")
        print(f"   - Viewpoints: {strategy.viewpoint_count}")
        print(f"   - Angles: {strategy.optimal_angles}")
        
        # Test multi-view detection
        needs_multiview = analyzer.should_use_multiview_observation(mock_object)
        print(f"✅ Needs multi-view: {needs_multiview}")
        
        return True
        
    except Exception as e:
        print(f"❌ Geometric analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_heuristic_detector_standalone():
    """Test heuristic detector without AI2-THOR controller."""
    print("\n🔍 Testing heuristic detector standalone...")
    
    try:
        from spatial_enhancement.heuristic_detector import HeuristicAmbiguityDetector
        from spatial_enhancement.spatial_calculator import SpatialRelationCalculator
        
        # Mock objects
        mock_objects = [
            {
                'objectId': 'Book_1',
                'objectType': 'Book',
                'position': {'x': 1.0, 'y': 0.5, 'z': 2.0},
                'visible': True
            },
            {
                'objectId': 'Book_2',
                'objectType': 'Book', 
                'position': {'x': -1.0, 'y': 0.5, 'z': 2.0},
                'visible': True
            }
        ]
        
        # Create detector with spatial calculator
        calculator = SpatialRelationCalculator()
        detector = HeuristicAmbiguityDetector(calculator)
        
        # Test ambiguity detection
        result = detector.detect_ambiguity("拿起左边的书", mock_objects)
        print(f"✅ Ambiguity detection result:")
        print(f"   - Has ambiguity: {result.has_ambiguity}")
        print(f"   - Reason: {result.reason}")
        print(f"   - Selected object: {result.selected_object_id}")
        print(f"   - Confidence: {result.confidence:.2f}")
        
        # Test heuristic selection
        selection = detector.heuristic_object_selection("拿起书", mock_objects)
        print(f"✅ Heuristic selection: {selection.selected_object_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Heuristic detector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_controller_with_cloud_rendering():
    """Test AI2-THOR controller with cloud rendering to avoid display issues."""
    print("\n🔍 Testing AI2-THOR controller with cloud rendering...")
    
    try:
        from ai2thor.controller import Controller
        from ai2thor.platform import CloudRendering
        
        # Try cloud rendering to avoid display issues
        print("   Attempting cloud rendering...")
        controller = Controller(
            platform=CloudRendering,
            scene='FloorPlan1',
            headless=True,
            width=400,
            height=300
        )
        
        print("✅ Controller created with cloud rendering")
        
        # Test basic functionality
        event = controller.step(dict(action='Pass'))
        print(f"✅ Basic controller action successful: {event.metadata['lastActionSuccess']}")
        
        # Test enhanced agent creation
        from evaluate.ai2thor_engine.EnhancedRocAgent import EnhancedRocAgent
        agent = EnhancedRocAgent(controller, scene='FloorPlan1')
        print("✅ Enhanced agent created successfully")
        
        # Test enhancement stats
        stats = agent.get_enhancement_stats()
        print(f"✅ Enhancement stats: {stats}")
        
        controller.stop()
        print("✅ Controller stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Controller test failed: {e}")
        print("   This is likely due to display/X11 issues in the environment")
        return False

def test_mock_server_integration():
    """Test the mock server integration."""
    print("\n🔍 Testing mock server integration...")
    
    try:
        # Import the mock server
        from simple_mock_server import MockVLMHandler
        print("✅ Mock server imported successfully")
        
        # Test basic handler functionality
        handler = MockVLMHandler()
        
        # Test response generation
        mock_request = {
            "messages": [
                {"role": "user", "content": "navigate to the book on the left"}
            ]
        }
        
        response = handler.generate_response(mock_request)
        print(f"✅ Mock server response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock server test failed: {e}")
        return False

def run_comprehensive_tests():
    """Run all tests and provide a summary."""
    print("🧪 Starting comprehensive spatial enhancement tests...")
    print("=" * 60)
    
    test_results = {}
    
    # Run all tests
    test_results['module_imports'] = test_module_imports()
    test_results['evaluate_integration'] = test_evaluate_integration()
    test_results['spatial_calculator'] = test_spatial_calculator_standalone()
    test_results['geometric_analyzer'] = test_geometric_analyzer_standalone()
    test_results['heuristic_detector'] = test_heuristic_detector_standalone()
    test_results['controller_cloud'] = test_controller_with_cloud_rendering()
    test_results['mock_server'] = test_mock_server_integration()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    # Provide recommendations
    print("\n🔧 RECOMMENDATIONS:")
    print("=" * 30)
    
    if test_results['module_imports'] and test_results['evaluate_integration']:
        print("✅ Spatial enhancement modules are properly integrated")
    else:
        print("❌ Module integration issues detected")
    
    if test_results['spatial_calculator'] and test_results['geometric_analyzer'] and test_results['heuristic_detector']:
        print("✅ Core spatial reasoning functionality works")
    else:
        print("❌ Core functionality issues detected")
    
    if not test_results['controller_cloud']:
        print("⚠️  AI2-THOR controller issues detected:")
        print("   - Try running with CloudRendering platform")
        print("   - Check DISPLAY environment variable")
        print("   - Consider using xvfb for headless environments")
        print("   - Use the mock server for testing without AI2-THOR")
    
    if test_results['mock_server']:
        print("✅ Mock server available as fallback for testing")
    
    return test_results

def provide_workaround_solutions():
    """Provide specific workaround solutions for common issues."""
    print("\n🛠️  WORKAROUND SOLUTIONS:")
    print("=" * 40)
    
    print("1. For X11/Display issues:")
    print("   export DISPLAY=:0")
    print("   # or use xvfb:")
    print("   xvfb-run -a python your_script.py")
    
    print("\n2. For testing without AI2-THOR:")
    print("   python simple_mock_server.py  # Start mock server")
    print("   # Then run your evaluation with MODE='LOCAL'")
    
    print("\n3. For evaluation with enhancements:")
    print("   python evaluate/evaluate_enhanced.py")
    print("   # Uses EnhancedRocAgent with fallback to original")
    
    print("\n4. For cloud rendering:")
    print("   # Modify controller creation to use CloudRendering")
    print("   from ai2thor.platform import CloudRendering")
    print("   controller = Controller(platform=CloudRendering, ...)")

if __name__ == "__main__":
    test_results = run_comprehensive_tests()
    provide_workaround_solutions()
    
    # Save test results
    results_file = Path("test_results.json")
    with open(results_file, "w") as f:
        json.dump(test_results, f, indent=2)
    print(f"\n📄 Test results saved to {results_file}")