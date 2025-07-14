"""Testing framework for spatial enhancement modules."""

import json
import time
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

@dataclass
class TestScenario:
    """Represents a test scenario for spatial reasoning."""
    scenario_id: str
    scene_name: str
    description: str
    instruction: str
    candidate_objects: List[Dict[str, Any]]
    expected_object_id: Optional[str]
    expected_confidence_threshold: float
    test_type: str  # "ambiguity", "spatial", "geometric"
    metadata: Dict[str, Any]

@dataclass 
class TestResult:
    """Results from running a test scenario."""
    scenario_id: str
    success: bool
    selected_object_id: Optional[str]
    confidence: float
    execution_time: float
    error_message: Optional[str]
    enhancement_used: bool
    detailed_metrics: Dict[str, Any]

class TestType(str, Enum):
    """Types of tests in the framework."""
    AMBIGUITY_RESOLUTION = "ambiguity"
    SPATIAL_CALCULATION = "spatial"  
    GEOMETRIC_ANALYSIS = "geometric"
    INTEGRATION = "integration"

class SpatialEnhancementTestFramework:
    """Test framework for spatial enhancement modules."""
    
    def __init__(self):
        """Initialize the test framework."""
        self.test_scenarios = []
        self.test_results = []
        self.baseline_results = []
        
    def create_test_scenarios(self) -> List[TestScenario]:
        """Create a comprehensive set of test scenarios.
        
        Returns:
            List of test scenarios
        """
        scenarios = []
        
        # Multi-book scenario for ambiguity testing
        scenarios.extend(self._create_multi_book_scenarios())
        
        # Large object scenarios for geometric testing
        scenarios.extend(self._create_large_object_scenarios())
        
        # Spatial relationship scenarios
        scenarios.extend(self._create_spatial_relationship_scenarios())
        
        # Complex integration scenarios
        scenarios.extend(self._create_integration_scenarios())
        
        self.test_scenarios = scenarios
        return scenarios
    
    def _create_multi_book_scenarios(self) -> List[TestScenario]:
        """Create scenarios with multiple books for ambiguity testing."""
        return [
            TestScenario(
                scenario_id="multi_book_001",
                scene_name="FloorPlan1",
                description="Three books in kitchen - ambiguous reference",
                instruction="拿起书",  # "pick up book" - ambiguous
                candidate_objects=[
                    {
                        "objectId": "Book|-00.47|+01.15|+00.48",
                        "objectType": "Book",
                        "position": {"x": -0.47, "y": 1.15, "z": 0.48},
                        "visible": True,
                        "parentReceptacles": ["CounterTop|-00.08|+01.15|00.00"]
                    },
                    {
                        "objectId": "Book|+01.23|+00.91|+00.31", 
                        "objectType": "Book",
                        "position": {"x": 1.23, "y": 0.91, "z": 0.31},
                        "visible": True,
                        "parentReceptacles": ["DiningTable|+01.23|+00.00|+00.31"]
                    },
                    {
                        "objectId": "Book|+02.10|+01.45|+00.15",
                        "objectType": "Book", 
                        "position": {"x": 2.10, "y": 1.45, "z": 0.15},
                        "visible": False,
                        "parentReceptacles": ["Shelf|+02.10|+01.45|+00.15"]
                    }
                ],
                expected_object_id=None,  # Should ask for clarification
                expected_confidence_threshold=0.5,
                test_type=TestType.AMBIGUITY_RESOLUTION,
                metadata={"requires_clarification": True}
            ),
            TestScenario(
                scenario_id="multi_book_002", 
                scene_name="FloorPlan1",
                description="Three books - spatial reference to left book",
                instruction="拿起左边的书",  # "pick up the left book"
                candidate_objects=[
                    {
                        "objectId": "Book|-00.47|+01.15|+00.48",
                        "objectType": "Book",
                        "position": {"x": -0.47, "y": 1.15, "z": 0.48},
                        "visible": True,
                        "parentReceptacles": ["CounterTop|-00.08|+01.15|00.00"]
                    },
                    {
                        "objectId": "Book|+01.23|+00.91|+00.31",
                        "objectType": "Book", 
                        "position": {"x": 1.23, "y": 0.91, "z": 0.31},
                        "visible": True,
                        "parentReceptacles": ["DiningTable|+01.23|+00.00|+00.31"]
                    },
                    {
                        "objectId": "Book|+02.10|+01.45|+00.15",
                        "objectType": "Book",
                        "position": {"x": 2.10, "y": 1.45, "z": 0.15}, 
                        "visible": True,
                        "parentReceptacles": ["Shelf|+02.10|+01.45|+00.15"]
                    }
                ],
                expected_object_id="Book|-00.47|+01.15|+00.48",  # Leftmost book
                expected_confidence_threshold=0.7,
                test_type=TestType.SPATIAL_CALCULATION,
                metadata={"spatial_constraint": "left"}
            ),
            TestScenario(
                scenario_id="multi_book_003",
                scene_name="FloorPlan1", 
                description="Three books - container reference",
                instruction="拿起桌上的书",  # "pick up the book on the table"
                candidate_objects=[
                    {
                        "objectId": "Book|-00.47|+01.15|+00.48",
                        "objectType": "Book",
                        "position": {"x": -0.47, "y": 1.15, "z": 0.48},
                        "visible": True,
                        "parentReceptacles": ["CounterTop|-00.08|+01.15|00.00"]
                    },
                    {
                        "objectId": "Book|+01.23|+00.91|+00.31",
                        "objectType": "Book",
                        "position": {"x": 1.23, "y": 0.91, "z": 0.31},
                        "visible": True,
                        "parentReceptacles": ["DiningTable|+01.23|+00.00|+00.31"]
                    },
                    {
                        "objectId": "Book|+02.10|+01.45|+00.15",
                        "objectType": "Book",
                        "position": {"x": 2.10, "y": 1.45, "z": 0.15},
                        "visible": True,
                        "parentReceptacles": ["Shelf|+02.10|+01.45|+00.15"]
                    }
                ],
                expected_object_id="Book|+01.23|+00.91|+00.31",  # Book on dining table
                expected_confidence_threshold=0.8,
                test_type=TestType.SPATIAL_CALCULATION,
                metadata={"container_constraint": "table"}
            )
        ]
    
    def _create_large_object_scenarios(self) -> List[TestScenario]:
        """Create scenarios with large objects for geometric testing."""
        return [
            TestScenario(
                scenario_id="large_sofa_001",
                scene_name="FloorPlan201",
                description="L-shaped sofa observation strategy",
                instruction="observe sofa",
                candidate_objects=[
                    {
                        "objectId": "Sofa|+02.25|+00.57|+01.50",
                        "objectType": "Sofa",
                        "position": {"x": 2.25, "y": 0.57, "z": 1.50},
                        "visible": True,
                        "axisAlignedBoundingBox": {
                            "center": {"x": 2.25, "y": 0.57, "z": 1.50},
                            "size": {"x": 2.5, "y": 0.8, "z": 1.2}
                        },
                        "rotation": {"x": 0, "y": 0, "z": 0}
                    }
                ],
                expected_object_id="Sofa|+02.25|+00.57|+01.50",
                expected_confidence_threshold=0.9,
                test_type=TestType.GEOMETRIC_ANALYSIS,
                metadata={"requires_multiview": True, "expected_viewpoints": 3}
            ),
            TestScenario(
                scenario_id="small_cup_001", 
                scene_name="FloorPlan1",
                description="Small cup single view strategy",
                instruction="observe cup",
                candidate_objects=[
                    {
                        "objectId": "Cup|+00.25|+01.15|+00.30",
                        "objectType": "Cup",
                        "position": {"x": 0.25, "y": 1.15, "z": 0.30},
                        "visible": True,
                        "axisAlignedBoundingBox": {
                            "center": {"x": 0.25, "y": 1.15, "z": 0.30},
                            "size": {"x": 0.08, "y": 0.12, "z": 0.08}
                        },
                        "rotation": {"x": 0, "y": 0, "z": 0}
                    }
                ],
                expected_object_id="Cup|+00.25|+01.15|+00.30",
                expected_confidence_threshold=0.95,
                test_type=TestType.GEOMETRIC_ANALYSIS,
                metadata={"requires_multiview": False, "expected_viewpoints": 1}
            )
        ]
    
    def _create_spatial_relationship_scenarios(self) -> List[TestScenario]:
        """Create scenarios for testing spatial relationship calculations."""
        return [
            TestScenario(
                scenario_id="spatial_proximity_001",
                scene_name="FloorPlan1",
                description="Near vs far object selection",
                instruction="get the cup near me",
                candidate_objects=[
                    {
                        "objectId": "Cup|+00.25|+01.15|+00.30",
                        "objectType": "Cup", 
                        "position": {"x": 0.25, "y": 1.15, "z": 0.30},
                        "visible": True
                    },
                    {
                        "objectId": "Cup|+03.50|+01.15|+02.80",
                        "objectType": "Cup",
                        "position": {"x": 3.50, "y": 1.15, "z": 2.80},
                        "visible": True
                    }
                ],
                expected_object_id="Cup|+00.25|+01.15|+00.30",  # Closer cup
                expected_confidence_threshold=0.8,
                test_type=TestType.SPATIAL_CALCULATION,
                metadata={"spatial_constraint": "near"}
            ),
            TestScenario(
                scenario_id="spatial_direction_001",
                scene_name="FloorPlan1", 
                description="Directional object selection",
                instruction="get the cup on the right",
                candidate_objects=[
                    {
                        "objectId": "Cup|+00.25|+01.15|+00.30",
                        "objectType": "Cup",
                        "position": {"x": 0.25, "y": 1.15, "z": 0.30},
                        "visible": True
                    },
                    {
                        "objectId": "Cup|+01.50|+01.15|+00.30", 
                        "objectType": "Cup",
                        "position": {"x": 1.50, "y": 1.15, "z": 0.30},
                        "visible": True
                    }
                ],
                expected_object_id="Cup|+01.50|+01.15|+00.30",  # Right cup
                expected_confidence_threshold=0.8,
                test_type=TestType.SPATIAL_CALCULATION,
                metadata={"spatial_constraint": "right"}
            )
        ]
    
    def _create_integration_scenarios(self) -> List[TestScenario]:
        """Create scenarios for testing end-to-end integration."""
        return [
            TestScenario(
                scenario_id="integration_001",
                scene_name="FloorPlan1",
                description="Complex multi-constraint scenario",
                instruction="拿起右边桌子上的书",  # "pick up the book on the right table"
                candidate_objects=[
                    {
                        "objectId": "Book|-00.47|+01.15|+00.48",
                        "objectType": "Book",
                        "position": {"x": -0.47, "y": 1.15, "z": 0.48},
                        "visible": True,
                        "parentReceptacles": ["CounterTop|-00.08|+01.15|00.00"]
                    },
                    {
                        "objectId": "Book|+01.23|+00.91|+00.31",
                        "objectType": "Book",
                        "position": {"x": 1.23, "y": 0.91, "z": 0.31},
                        "visible": True,
                        "parentReceptacles": ["DiningTable|+01.23|+00.00|+00.31"]
                    }
                ],
                expected_object_id="Book|+01.23|+00.91|+00.31",  # Book on right table
                expected_confidence_threshold=0.7,
                test_type=TestType.INTEGRATION,
                metadata={"constraints": ["direction", "container"]}
            )
        ]
    
    def run_test_suite(self, enhancement_modules: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete test suite.
        
        Args:
            enhancement_modules: Dictionary with spatial calculator, ambiguity detector, etc.
            
        Returns:
            Comprehensive test results
        """
        if not self.test_scenarios:
            self.create_test_scenarios()
        
        results = {
            'total_scenarios': len(self.test_scenarios),
            'passed': 0,
            'failed': 0,
            'execution_time': 0,
            'results_by_type': {},
            'detailed_results': []
        }
        
        start_time = time.time()
        
        for scenario in self.test_scenarios:
            test_result = self._run_single_test(scenario, enhancement_modules)
            results['detailed_results'].append(test_result)
            
            if test_result.success:
                results['passed'] += 1
            else:
                results['failed'] += 1
            
            # Group by test type
            test_type = scenario.test_type
            if test_type not in results['results_by_type']:
                results['results_by_type'][test_type] = {'passed': 0, 'failed': 0, 'total': 0}
            
            results['results_by_type'][test_type]['total'] += 1
            if test_result.success:
                results['results_by_type'][test_type]['passed'] += 1
            else:
                results['results_by_type'][test_type]['failed'] += 1
        
        results['execution_time'] = time.time() - start_time
        results['success_rate'] = results['passed'] / results['total_scenarios'] if results['total_scenarios'] > 0 else 0
        
        return results
    
    def _run_single_test(self, scenario: TestScenario, 
                        enhancement_modules: Dict[str, Any]) -> TestResult:
        """Run a single test scenario.
        
        Args:
            scenario: Test scenario to run
            enhancement_modules: Enhancement modules to test
            
        Returns:
            Test result
        """
        start_time = time.time()
        
        try:
            if scenario.test_type == TestType.AMBIGUITY_RESOLUTION:
                return self._test_ambiguity_resolution(scenario, enhancement_modules)
            elif scenario.test_type == TestType.SPATIAL_CALCULATION:
                return self._test_spatial_calculation(scenario, enhancement_modules)
            elif scenario.test_type == TestType.GEOMETRIC_ANALYSIS:
                return self._test_geometric_analysis(scenario, enhancement_modules)
            elif scenario.test_type == TestType.INTEGRATION:
                return self._test_integration(scenario, enhancement_modules)
            else:
                return TestResult(
                    scenario_id=scenario.scenario_id,
                    success=False,
                    selected_object_id=None,
                    confidence=0.0,
                    execution_time=time.time() - start_time,
                    error_message=f"Unknown test type: {scenario.test_type}",
                    enhancement_used=False,
                    detailed_metrics={}
                )
                
        except Exception as e:
            return TestResult(
                scenario_id=scenario.scenario_id,
                success=False,
                selected_object_id=None,
                confidence=0.0,
                execution_time=time.time() - start_time,
                error_message=str(e),
                enhancement_used=False,
                detailed_metrics={}
            )
    
    def _test_ambiguity_resolution(self, scenario: TestScenario,
                                 enhancement_modules: Dict[str, Any]) -> TestResult:
        """Test ambiguity resolution capability."""
        start_time = time.time()
        
        ambiguity_detector = enhancement_modules.get('ambiguity_detector')
        if not ambiguity_detector:
            return TestResult(
                scenario_id=scenario.scenario_id,
                success=False,
                selected_object_id=None,
                confidence=0.0,
                execution_time=time.time() - start_time,
                error_message="Ambiguity detector not available",
                enhancement_used=False,
                detailed_metrics={}
            )
        
        # Run ambiguity detection
        ambiguity_result = ambiguity_detector.detect_ambiguity(
            scenario.instruction, scenario.candidate_objects
        )
        
        # Evaluate results
        success = False
        if scenario.metadata.get("requires_clarification", False):
            # Should detect ambiguity and ask for clarification
            success = (ambiguity_result.has_ambiguity and 
                      ambiguity_result.clarification_question is not None)
        else:
            # Should resolve successfully
            success = (not ambiguity_result.has_ambiguity and
                      ambiguity_result.selected_object_id == scenario.expected_object_id and
                      ambiguity_result.confidence >= scenario.expected_confidence_threshold)
        
        return TestResult(
            scenario_id=scenario.scenario_id,
            success=success,
            selected_object_id=ambiguity_result.selected_object_id,
            confidence=ambiguity_result.confidence,
            execution_time=time.time() - start_time,
            error_message=None,
            enhancement_used=True,
            detailed_metrics={
                'has_ambiguity': ambiguity_result.has_ambiguity,
                'reason': ambiguity_result.reason,
                'clarification_question': ambiguity_result.clarification_question
            }
        )
    
    def _test_spatial_calculation(self, scenario: TestScenario,
                                enhancement_modules: Dict[str, Any]) -> TestResult:
        """Test spatial calculation capability."""
        start_time = time.time()
        
        spatial_calculator = enhancement_modules.get('spatial_calculator')
        if not spatial_calculator:
            return TestResult(
                scenario_id=scenario.scenario_id,
                success=False,
                selected_object_id=None,
                confidence=0.0,
                execution_time=time.time() - start_time,
                error_message="Spatial calculator not available",
                enhancement_used=False,
                detailed_metrics={}
            )
        
        # Test spatial relationship calculation
        best_match, confidence = spatial_calculator.find_best_spatial_match(
            scenario.candidate_objects, scenario.instruction
        )
        
        success = (best_match == scenario.expected_object_id and
                  confidence >= scenario.expected_confidence_threshold)
        
        return TestResult(
            scenario_id=scenario.scenario_id,
            success=success,
            selected_object_id=best_match,
            confidence=confidence,
            execution_time=time.time() - start_time,
            error_message=None,
            enhancement_used=True,
            detailed_metrics={
                'spatial_constraints': spatial_calculator.extract_spatial_constraints(scenario.instruction)
            }
        )
    
    def _test_geometric_analysis(self, scenario: TestScenario,
                               enhancement_modules: Dict[str, Any]) -> TestResult:
        """Test geometric analysis capability."""
        start_time = time.time()
        
        geometric_analyzer = enhancement_modules.get('geometric_analyzer')
        if not geometric_analyzer:
            return TestResult(
                scenario_id=scenario.scenario_id,
                success=False,
                selected_object_id=None,
                confidence=0.0,
                execution_time=time.time() - start_time,
                error_message="Geometric analyzer not available",
                enhancement_used=False,
                detailed_metrics={}
            )
        
        # Test observation strategy analysis
        target_object = scenario.candidate_objects[0]
        strategy = geometric_analyzer.analyze_observation_requirements(target_object)
        
        # Check if strategy matches expectations
        requires_multiview = scenario.metadata.get("requires_multiview", False)
        expected_viewpoints = scenario.metadata.get("expected_viewpoints", 1)
        
        success = True
        if requires_multiview:
            success = (strategy.strategy_type in ["multi_view", "adaptive"] and
                      strategy.viewpoint_count >= expected_viewpoints)
        else:
            success = (strategy.strategy_type == "single_view" and
                      strategy.viewpoint_count == 1)
        
        return TestResult(
            scenario_id=scenario.scenario_id,
            success=success,
            selected_object_id=target_object.get('objectId'),
            confidence=1.0 if success else 0.0,
            execution_time=time.time() - start_time,
            error_message=None,
            enhancement_used=True,
            detailed_metrics={
                'strategy_type': strategy.strategy_type,
                'viewpoint_count': strategy.viewpoint_count,
                'optimal_distance': strategy.optimal_distance
            }
        )
    
    def _test_integration(self, scenario: TestScenario,
                        enhancement_modules: Dict[str, Any]) -> TestResult:
        """Test end-to-end integration."""
        start_time = time.time()
        
        # Use both spatial calculator and ambiguity detector
        spatial_calculator = enhancement_modules.get('spatial_calculator')
        ambiguity_detector = enhancement_modules.get('ambiguity_detector')
        
        if not spatial_calculator or not ambiguity_detector:
            return TestResult(
                scenario_id=scenario.scenario_id,
                success=False,
                selected_object_id=None,
                confidence=0.0,
                execution_time=time.time() - start_time,
                error_message="Required modules not available",
                enhancement_used=False,
                detailed_metrics={}
            )
        
        # Run full disambiguation pipeline
        ambiguity_result = ambiguity_detector.heuristic_object_selection(
            scenario.instruction, scenario.candidate_objects
        )
        
        success = (ambiguity_result.selected_object_id == scenario.expected_object_id and
                  ambiguity_result.confidence >= scenario.expected_confidence_threshold)
        
        return TestResult(
            scenario_id=scenario.scenario_id,
            success=success,
            selected_object_id=ambiguity_result.selected_object_id,
            confidence=ambiguity_result.confidence,
            execution_time=time.time() - start_time,
            error_message=None,
            enhancement_used=True,
            detailed_metrics={
                'has_ambiguity': ambiguity_result.has_ambiguity,
                'reason': ambiguity_result.reason
            }
        )
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable test report.
        
        Args:
            results: Test results from run_test_suite
            
        Returns:
            Formatted test report
        """
        report = []
        report.append("=" * 60)
        report.append("SPATIAL ENHANCEMENT TEST REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        report.append(f"Total Scenarios: {results['total_scenarios']}")
        report.append(f"Passed: {results['passed']}")
        report.append(f"Failed: {results['failed']}")
        report.append(f"Success Rate: {results['success_rate']:.2%}")
        report.append(f"Execution Time: {results['execution_time']:.2f}s")
        report.append("")
        
        # Results by type
        report.append("RESULTS BY TEST TYPE:")
        report.append("-" * 30)
        for test_type, type_results in results['results_by_type'].items():
            total = type_results['total']
            passed = type_results['passed']
            rate = passed / total if total > 0 else 0
            report.append(f"{test_type}: {passed}/{total} ({rate:.2%})")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS:")
        report.append("-" * 30)
        for result in results['detailed_results']:
            status = "PASS" if result.success else "FAIL"
            report.append(f"[{status}] {result.scenario_id}: confidence={result.confidence:.2f}, time={result.execution_time:.3f}s")
            if result.error_message:
                report.append(f"    Error: {result.error_message}")
        
        return "\n".join(report)
    
    def save_results(self, results: Dict[str, Any], filepath: str):
        """Save test results to JSON file.
        
        Args:
            results: Test results to save
            filepath: Output file path
        """
        # Convert TestResult dataclasses to dicts for JSON serialization
        serializable_results = results.copy()
        serializable_results['detailed_results'] = [
            asdict(result) for result in results['detailed_results']
        ]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)