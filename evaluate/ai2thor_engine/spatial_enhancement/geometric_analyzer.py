"""GeometricAnalyzer for dynamic observation distance calculation based on object geometry."""

import math
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class ObservationStrategy:
    """Defines observation strategy for an object."""
    strategy_type: str  # "single_view", "multi_view", "adaptive"
    optimal_distance: float
    optimal_angles: List[float]  # in degrees
    viewpoint_count: int
    coverage_threshold: float
    approach_distance: float  # for navigation

class ObjectGeometry:
    """Geometric properties of an object."""
    
    def __init__(self, obj_metadata: Dict[str, Any]):
        """Initialize from AI2-THOR object metadata.
        
        Args:
            obj_metadata: Object metadata from AI2-THOR
        """
        self.object_id = obj_metadata.get('objectId', 'unknown')
        self.object_type = obj_metadata.get('objectType', 'unknown')
        
        # Extract AABB information
        aabb = obj_metadata.get('axisAlignedBoundingBox', {})
        size = aabb.get('size', {'x': 1.0, 'y': 1.0, 'z': 1.0})
        center = aabb.get('center', {'x': 0.0, 'y': 0.0, 'z': 0.0})
        
        self.width = size.get('x', 1.0)
        self.height = size.get('y', 1.0) 
        self.depth = size.get('z', 1.0)
        self.center = np.array([center.get('x', 0), center.get('y', 0), center.get('z', 0)])
        
        # Calculate derived properties
        self.volume = self.width * self.height * self.depth
        self.surface_area = 2 * (self.width * self.height + self.width * self.depth + self.height * self.depth)
        self.max_dimension = max(self.width, self.height, self.depth)
        self.min_dimension = min(self.width, self.height, self.depth)
        self.aspect_ratio = self.max_dimension / self.min_dimension if self.min_dimension > 0 else 1.0
        
        # Classify object shape
        self.shape_type = self._classify_shape()
        
    def _classify_shape(self) -> str:
        """Classify object shape based on dimensions."""
        if self.aspect_ratio <= 1.5:
            return "compact"  # roughly cubic/spherical
        elif self.aspect_ratio <= 3.0:
            return "elongated"  # rectangular, moderately stretched
        else:
            return "linear"  # very stretched, like a long table

class GeometricAnalyzer:
    """Analyzes object geometry to determine optimal observation strategies."""
    
    def __init__(self):
        """Initialize with configurable thresholds."""
        # Configuration parameters
        self.small_object_volume_threshold = 0.2
        self.small_object_surface_threshold = 0.5
        self.large_object_volume_threshold = 1.0
        self.large_object_surface_threshold = 1.0
        self.very_large_volume_threshold = 2.0
        
        # Distance calculation parameters
        self.base_distance_factor = 1.5  # Base multiplier for object size
        self.min_observation_distance = 0.5
        self.max_observation_distance = 3.0
        
        # Coverage and viewpoint parameters
        self.default_coverage_threshold = 0.85
        self.max_viewpoints = 6
        
    def analyze_observation_requirements(self, obj_metadata: Dict[str, Any]) -> ObservationStrategy:
        """Analyze object and determine optimal observation strategy.
        
        Args:
            obj_metadata: AI2-THOR object metadata
            
        Returns:
            ObservationStrategy defining how to observe the object
        """
        geometry = ObjectGeometry(obj_metadata)
        
        # Determine strategy based on object characteristics
        if self._is_small_object(geometry):
            return self._single_view_strategy(geometry)
        elif self._is_large_complex_object(geometry):
            return self._multi_view_strategy(geometry)
        else:
            return self._adaptive_strategy(geometry)
    
    def _is_small_object(self, geometry: ObjectGeometry) -> bool:
        """Check if object is small enough for single-view observation."""
        return (geometry.volume <= self.small_object_volume_threshold and 
                geometry.surface_area <= self.small_object_surface_threshold)
    
    def _is_large_complex_object(self, geometry: ObjectGeometry) -> bool:
        """Check if object requires multi-view observation."""
        return (geometry.volume > self.large_object_volume_threshold or
                geometry.surface_area > self.large_object_surface_threshold or
                geometry.max_dimension > 2.0 or
                geometry.aspect_ratio > 3.0)
    
    def _single_view_strategy(self, geometry: ObjectGeometry) -> ObservationStrategy:
        """Generate single-view observation strategy for small objects."""
        optimal_distance = self._calculate_optimal_distance(geometry)
        approach_distance = max(optimal_distance * 0.8, self.min_observation_distance)
        
        return ObservationStrategy(
            strategy_type="single_view",
            optimal_distance=optimal_distance,
            optimal_angles=[0.0],  # Front view
            viewpoint_count=1,
            coverage_threshold=0.95,  # High threshold for single view
            approach_distance=approach_distance
        )
    
    def _multi_view_strategy(self, geometry: ObjectGeometry) -> ObservationStrategy:
        """Generate multi-view observation strategy for large/complex objects."""
        optimal_distance = self._calculate_optimal_distance(geometry)
        
        # Calculate number of viewpoints based on object complexity
        viewpoint_count = self._calculate_required_viewpoints(geometry)
        
        # Generate viewing angles
        optimal_angles = self._generate_viewing_angles(geometry, viewpoint_count)
        
        # Adjust approach distance for large objects
        approach_distance = max(optimal_distance * 1.2, 1.0)
        
        return ObservationStrategy(
            strategy_type="multi_view",
            optimal_distance=optimal_distance,
            optimal_angles=optimal_angles,
            viewpoint_count=viewpoint_count,
            coverage_threshold=self.default_coverage_threshold,
            approach_distance=approach_distance
        )
    
    def _adaptive_strategy(self, geometry: ObjectGeometry) -> ObservationStrategy:
        """Generate adaptive strategy for medium-sized objects."""
        optimal_distance = self._calculate_optimal_distance(geometry)
        
        # Decide between 1-3 viewpoints based on object properties
        if geometry.aspect_ratio > 2.0:
            viewpoint_count = 3  # Elongated objects need more views
            optimal_angles = [0.0, 90.0, 270.0]  # Front and sides
        else:
            viewpoint_count = 2  # Compact objects need fewer views
            optimal_angles = [0.0, 180.0]  # Front and back
            
        approach_distance = optimal_distance * 0.9
        
        return ObservationStrategy(
            strategy_type="adaptive",
            optimal_distance=optimal_distance,
            optimal_angles=optimal_angles,
            viewpoint_count=viewpoint_count,
            coverage_threshold=0.80,  # Moderate threshold
            approach_distance=approach_distance
        )
    
    def _calculate_optimal_distance(self, geometry: ObjectGeometry) -> float:
        """Calculate optimal observation distance based on object size."""
        # Base distance proportional to object size
        size_factor = max(geometry.width, geometry.depth)
        base_distance = size_factor * self.base_distance_factor
        
        # Adjust for object height (vertical objects need more distance)
        if geometry.height > 1.5:
            height_factor = 1.0 + (geometry.height - 1.5) * 0.3
            base_distance *= height_factor
        
        # Adjust for shape complexity
        if geometry.shape_type == "linear":
            base_distance *= 1.3  # Need more distance for elongated objects
        elif geometry.shape_type == "compact":
            base_distance *= 0.9  # Can get closer to compact objects
        
        # Clamp to reasonable bounds
        return max(self.min_observation_distance, 
                  min(base_distance, self.max_observation_distance))
    
    def _calculate_required_viewpoints(self, geometry: ObjectGeometry) -> int:
        """Calculate number of viewpoints needed for adequate coverage."""
        # Base viewpoint count
        base_count = 2
        
        # Add viewpoints based on object characteristics
        if geometry.volume > self.very_large_volume_threshold:
            base_count += 2
        elif geometry.volume > self.large_object_volume_threshold:
            base_count += 1
        
        # Add viewpoints for complex shapes
        if geometry.aspect_ratio > 4.0:
            base_count += 2  # Very elongated objects
        elif geometry.aspect_ratio > 2.5:
            base_count += 1  # Moderately elongated
        
        # Add viewpoint for tall objects
        if geometry.height > 2.0:
            base_count += 1
        
        return min(base_count, self.max_viewpoints)
    
    def _generate_viewing_angles(self, geometry: ObjectGeometry, viewpoint_count: int) -> List[float]:
        """Generate optimal viewing angles for multi-view observation."""
        if viewpoint_count <= 1:
            return [0.0]
        
        # For elongated objects, focus on sides and ends
        if geometry.shape_type == "linear":
            if viewpoint_count >= 4:
                return [0.0, 90.0, 180.0, 270.0]  # Cardinal directions
            elif viewpoint_count == 3:
                return [0.0, 90.0, 270.0]  # Front and sides
            else:
                return [0.0, 180.0]  # Front and back
        
        # For compact objects, distribute evenly
        else:
            angle_step = 360.0 / viewpoint_count
            return [i * angle_step for i in range(viewpoint_count)]
    
    def get_enhanced_positioning_strategy(self, obj_metadata: Dict[str, Any], 
                                        candidate_positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Replace the fixed threshold logic in compute_closest_positions.
        
        Args:
            obj_metadata: Object metadata from AI2-THOR
            candidate_positions: Available positions for navigation
            
        Returns:
            Filtered and sorted list of optimal positions
        """
        strategy = self.analyze_observation_requirements(obj_metadata)
        geometry = ObjectGeometry(obj_metadata)
        
        item_position = obj_metadata.get('position', {'x': 0, 'y': 0, 'z': 0})
        
        # Filter positions based on optimal distance
        filtered_positions = []
        for position in candidate_positions:
            distance = math.sqrt(
                (position['x'] - item_position['x'])**2 + 
                (position['z'] - item_position['z'])**2
            )
            
            # Check if position is within acceptable range
            min_acceptable = strategy.approach_distance * 0.8
            max_acceptable = strategy.approach_distance * 1.5
            
            if min_acceptable <= distance <= max_acceptable:
                position['distance_to_object'] = distance
                position['distance_score'] = self._calculate_distance_score(
                    distance, strategy.approach_distance
                )
                filtered_positions.append(position)
        
        # If no positions in ideal range, expand search
        if not filtered_positions:
            for position in candidate_positions:
                distance = math.sqrt(
                    (position['x'] - item_position['x'])**2 + 
                    (position['z'] - item_position['z'])**2
                )
                position['distance_to_object'] = distance
                position['distance_score'] = self._calculate_distance_score(
                    distance, strategy.approach_distance
                )
                filtered_positions.append(position)
        
        # Sort by distance score (higher is better)
        filtered_positions.sort(key=lambda p: p['distance_score'], reverse=True)
        
        return filtered_positions
    
    def _calculate_distance_score(self, actual_distance: float, optimal_distance: float) -> float:
        """Calculate how good a distance is relative to the optimal distance."""
        if actual_distance <= 0:
            return 0.0
        
        # Calculate relative distance
        ratio = actual_distance / optimal_distance
        
        # Score function: peak at ratio=1, decreases as distance from optimal increases
        if ratio <= 1.0:
            # Closer than optimal: gradual decrease
            return ratio
        else:
            # Further than optimal: steeper decrease
            return max(0.0, 2.0 - ratio)
    
    def should_use_multiview_observation(self, obj_metadata: Dict[str, Any]) -> bool:
        """Quick check if object requires multi-view observation."""
        strategy = self.analyze_observation_requirements(obj_metadata)
        return strategy.strategy_type in ["multi_view", "adaptive"] and strategy.viewpoint_count > 1
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration parameters."""
        return {
            'small_object_volume_threshold': self.small_object_volume_threshold,
            'small_object_surface_threshold': self.small_object_surface_threshold,
            'large_object_volume_threshold': self.large_object_volume_threshold,
            'large_object_surface_threshold': self.large_object_surface_threshold,
            'very_large_volume_threshold': self.very_large_volume_threshold,
            'base_distance_factor': self.base_distance_factor,
            'min_observation_distance': self.min_observation_distance,
            'max_observation_distance': self.max_observation_distance,
            'default_coverage_threshold': self.default_coverage_threshold,
            'max_viewpoints': self.max_viewpoints
        }
    
    def update_configuration(self, config: Dict[str, Any]):
        """Update configuration parameters."""
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)