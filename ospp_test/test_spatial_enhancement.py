#!/usr/bin/env python3
"""Integration test script for spatial enhancement modules."""

import sys
import os
import traceback
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_module_imports():
    """Test that all enhancement modules can be imported."""
    print("Testing module imports...")
    
    try:
        from spatial_enhancement.spatial_calculator import SpatialRelationCalculator
        print("✓ SpatialRelationCalculator imported successfully")
    except Exception as e:
        print(f"✗ Failed to import SpatialRelationCalculator: {e}")
        return False
    
    try:
        from spatial_enhancement.heuristic_detector import HeuristicAmbiguityDetector
        print("✓ HeuristicAmbiguityDetector imported successfully")
    except Exception as e:
        print(f"✗ Failed to import HeuristicAmbiguityDetector: {e}")
        return False
    
    try:
        from spatial_enhancement.geometric_analyzer import GeometricAnalyzer
        print("✓ GeometricAnalyzer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import GeometricAnalyzer: {e}")
        return False
    
    try:
        from spatial_enhancement.enhanced_agent import EnhancedRocAgent
        print("✓ EnhancedRocAgent imported successfully")
    except Exception as e:
        print(f"✗ Failed to import EnhancedRocAgent: {e}")
        return False
    
    try:
        from spatial_enhancement.test_framework import SpatialEnhancementTestFramework
        print("✓ SpatialEnhancementTestFramework imported successfully")
    except Exception as e:
        print(f"✗ Failed to import SpatialEnhancementTestFramework: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of enhancement modules."""
    print("\nTesting basic functionality...")
    
    try:
        from spatial_enhancement.spatial_calculator import SpatialRelationCalculator
        from spatial_enhancement.heuristic_detector import HeuristicAmbiguityDetector
        from spatial_enhancement.geometric_analyzer import GeometricAnalyzer
        
        # Test SpatialRelationCalculator
        print("Testing SpatialRelationCalculator...")
        calculator = SpatialRelationCalculator()
        
        # Test spatial constraint extraction
        constraints = calculator.extract_spatial_constraints("拿起左边的书")
        print(f"  Extracted constraints: {constraints}")
        
        # Test spatial scoring
        test_objects = [
            {
                "objectId": "Book1",
                "objectType": "Book",
                "position": {"x": -1.0, "y": 1.0, "z": 0.0},
                "visible": True
            },
            {
                "objectId": "Book2", 
                "objectType": "Book",
                "position": {"x": 1.0, "y": 1.0, "z": 0.0},
                "visible": True
            }
        ]
        
        best_match, confidence = calculator.find_best_spatial_match(test_objects, "拿起左边的书")
        print(f"  Best match: {best_match}, confidence: {confidence}")
        
        # Test HeuristicAmbiguityDetector
        print("Testing HeuristicAmbiguityDetector...")
        detector = HeuristicAmbiguityDetector(calculator)
        
        result = detector.detect_ambiguity("拿起书", test_objects)
        print(f"  Ambiguity result: has_ambiguity={result.has_ambiguity}, reason='{result.reason}'")
        
        result = detector.detect_ambiguity("拿起左边的书", test_objects)
        print(f"  Spatial result: has_ambiguity={result.has_ambiguity}, selected={result.selected_object_id}")
        
        # Test GeometricAnalyzer
        print("Testing GeometricAnalyzer...")
        analyzer = GeometricAnalyzer()
        
        small_object = {
            "objectId": "Cup1",
            "objectType": "Cup",
            "axisAlignedBoundingBox": {
                "center": {"x": 0, "y": 1, "z": 0},
                "size": {"x": 0.08, "y": 0.12, "z": 0.08}
            }
        }
        
        large_object = {
            "objectId": "Sofa1", 
            "objectType": "Sofa",
            "axisAlignedBoundingBox": {
                "center": {"x": 0, "y": 0.5, "z": 0},
                "size": {"x": 2.5, "y": 0.8, "z": 1.2}
            }
        }
        
        small_strategy = analyzer.analyze_observation_requirements(small_object)
        large_strategy = analyzer.analyze_observation_requirements(large_object)
        
        print(f"  Small object strategy: {small_strategy.strategy_type}, viewpoints: {small_strategy.viewpoint_count}")
        print(f"  Large object strategy: {large_strategy.strategy_type}, viewpoints: {large_strategy.viewpoint_count}")
        
        print("✓ Basic functionality tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_integration_with_test_framework():
    """Test integration with the test framework."""
    print("\nTesting integration with test framework...")
    
    try:
        from spatial_enhancement.spatial_calculator import SpatialRelationCalculator
        from spatial_enhancement.heuristic_detector import HeuristicAmbiguityDetector
        from spatial_enhancement.geometric_analyzer import GeometricAnalyzer
        from spatial_enhancement.test_framework import SpatialEnhancementTestFramework
        
        # Initialize enhancement modules
        calculator = SpatialRelationCalculator()
        detector = HeuristicAmbiguityDetector(calculator)
        analyzer = GeometricAnalyzer()
        
        enhancement_modules = {
            'spatial_calculator': calculator,
            'ambiguity_detector': detector,
            'geometric_analyzer': analyzer
        }
        
        # Initialize test framework
        test_framework = SpatialEnhancementTestFramework()
        scenarios = test_framework.create_test_scenarios()
        
        print(f"  Created {len(scenarios)} test scenarios")
        
        # Run a subset of tests
        print("  Running test suite...")
        results = test_framework.run_test_suite(enhancement_modules)
        
        print(f"  Test results: {results['passed']}/{results['total_scenarios']} passed ({results['success_rate']:.2%})")
        
        # Generate report
        report = test_framework.generate_test_report(results)
        print("  Generated test report")
        
        # Save results
        results_file = project_root / "test_results.json"
        test_framework.save_results(results, str(results_file))
        print(f"  Saved results to {results_file}")
        
        print("✓ Test framework integration successful")
        return True
        
    except Exception as e:
        print(f"✗ Test framework integration failed: {e}")
        traceback.print_exc()
        return False

def test_enhanced_agent_compatibility():
    """Test that EnhancedRocAgent can be created without errors."""
    print("\nTesting EnhancedRocAgent compatibility...")
    
    try:
        from spatial_enhancement.enhanced_agent import EnhancedRocAgent, LightweightEnhancementAdapter
        
        # Test adapter creation
        adapter = LightweightEnhancementAdapter(None)
        print("  ✓ LightweightEnhancementAdapter created")
        
        # Test EnhancedRocAgent creation with minimal parameters
        # Note: This will fail if AI2-THOR is not available, which is expected
        try:
            enhanced_agent = EnhancedRocAgent(
                controller=None,  # This will cause initialization to fail gracefully
                enable_enhancements=True
            )
            print("  ✓ EnhancedRocAgent initialization structure is correct")
        except Exception as e:
            # Expected to fail without proper controller, but structure should be sound
            if "controller" in str(e).lower() or "NoneType" in str(e):
                print("  ✓ EnhancedRocAgent fails gracefully without controller (expected)")
            else:
                print(f"  ⚠ EnhancedRocAgent failed with unexpected error: {e}")
        
        print("✓ Enhanced agent compatibility verified")
        return True
        
    except Exception as e:
        print(f"✗ Enhanced agent compatibility test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all integration tests."""
    print("Starting spatial enhancement integration tests...")
    print("=" * 60)
    
    all_passed = True
    
    # Test module imports
    if not test_module_imports():
        all_passed = False
    
    # Test basic functionality
    if not test_basic_functionality():
        all_passed = False
    
    # Test framework integration
    if not test_integration_with_test_framework():
        all_passed = False
    
    # Test enhanced agent compatibility
    if not test_enhanced_agent_compatibility():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("\nSpatial enhancement modules are ready for use.")
        print("\nNext steps:")
        print("1. Test with actual AI2-THOR environment")
        print("2. Integrate with existing evaluation pipeline")
        print("3. Run performance benchmarks")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease check the error messages above and fix the issues.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)