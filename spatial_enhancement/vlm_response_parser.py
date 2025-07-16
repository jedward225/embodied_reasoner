"""VLM Response Parser for handling numbered object references like 'vase1', 'book2', etc."""

import re
import math
from typing import Dict, List, Any, Optional, Tuple

class VLMResponseParser:
    """Parse VLM responses that contain numbered object references."""
    
    def __init__(self):
        """Initialize the parser with regex patterns."""
        # Match patterns like 'vase1', 'book2', 'apple3', etc.
        self.number_pattern = re.compile(r'(\w+)(\d+)')
        # Match patterns like 'navigate to vase1', 'pick up book2', etc.
        self.action_pattern = re.compile(r'(?:navigate to|pick up|go to|get|take)?\s*(\w+)(\d+)', re.IGNORECASE)
        
    def parse_numbered_response(self, vlm_response: str, candidate_objects: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Parse VLM response for numbered object references.
        
        Args:
            vlm_response: The VLM response text
            candidate_objects: List of candidate objects to choose from
            
        Returns:
            Selected object dict or None if parsing fails
        """
        # Clean the response
        vlm_response = vlm_response.strip().lower()
        
        # Try action pattern first, then number pattern
        for pattern in [self.action_pattern, self.number_pattern]:
            match = pattern.search(vlm_response)
            if match:
                object_type = match.group(1)
                object_number = int(match.group(2))
                
                # Find objects of the specified type
                same_type_objects = [obj for obj in candidate_objects 
                                   if object_type in obj.get('objectType', '').lower()]
                
                if len(same_type_objects) >= object_number:
                    # Sort objects consistently and return the indexed one
                    sorted_objects = self.sort_objects_consistently(same_type_objects)
                    return sorted_objects[object_number - 1]  # 1-based indexing
        
        return None
    
    def sort_objects_consistently(self, objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort objects in a consistent manner for stable indexing.
        
        Args:
            objects: List of objects to sort
            
        Returns:
            Sorted list of objects
        """
        def get_position(obj):
            """Get position for sorting."""
            pos = obj.get('position', {})
            return (pos.get('x', 0), pos.get('z', 0))
        
        # Sort by position: left to right (x), then front to back (z)
        return sorted(objects, key=get_position)
    
    def contains_numbered_reference(self, response: str) -> bool:
        """Check if response contains numbered object references.
        
        Args:
            response: The response text to check
            
        Returns:
            True if numbered reference is found
        """
        return bool(self.number_pattern.search(response.lower()))
    
    def extract_object_info(self, response: str) -> Optional[Tuple[str, int]]:
        """Extract object type and number from response.
        
        Args:
            response: The response text
            
        Returns:
            Tuple of (object_type, number) or None
        """
        match = self.number_pattern.search(response.lower())
        if match:
            return match.group(1), int(match.group(2))
        return None


class SmartObjectSorting:
    """Smart object sorting strategies for consistent indexing."""
    
    def __init__(self):
        """Initialize sorting strategies."""
        self.sorting_strategies = {
            'spatial_left_to_right': self.sort_by_left_to_right,
            'distance_based': self.sort_by_distance,
            'visibility_based': self.sort_by_visibility,
            'default': self.sort_by_left_to_right
        }
    
    def sort_by_left_to_right(self, objects: List[Dict[str, Any]], 
                             agent_position: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Sort objects from left to right relative to agent or world coordinates.
        
        Args:
            objects: List of objects to sort
            agent_position: Optional agent position for relative sorting
            
        Returns:
            Sorted list of objects
        """
        if agent_position:
            # Calculate relative position to agent
            return sorted(objects, key=lambda obj: 
                self.calculate_relative_x_position(obj, agent_position)
            )
        else:
            # Use world coordinates
            return sorted(objects, key=lambda obj: obj.get('position', {}).get('x', 0))
    
    def sort_by_distance(self, objects: List[Dict[str, Any]], 
                        agent_position: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sort objects by distance from agent (nearest first).
        
        Args:
            objects: List of objects to sort
            agent_position: Agent position
            
        Returns:
            Sorted list of objects
        """
        return sorted(objects, key=lambda obj:
            self.calculate_distance(obj.get('position', {}), agent_position)
        )
    
    def sort_by_visibility(self, objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort objects by visibility (visible first).
        
        Args:
            objects: List of objects to sort
            
        Returns:
            Sorted list of objects
        """
        return sorted(objects, key=lambda obj: (
            not obj.get('visible', False),  # Visible objects first
            obj.get('position', {}).get('x', 0)  # Then by position
        ))
    
    def get_optimal_sorting_strategy(self, instruction: str) -> str:
        """Get the optimal sorting strategy based on instruction.
        
        Args:
            instruction: The instruction text
            
        Returns:
            Name of the optimal sorting strategy
        """
        instruction_lower = instruction.lower()
        
        if any(word in instruction_lower for word in ['left', 'right', 'beside', 'next']):
            return 'spatial_left_to_right'
        elif any(word in instruction_lower for word in ['near', 'close', 'closest']):
            return 'distance_based'
        elif any(word in instruction_lower for word in ['visible', 'see', 'look']):
            return 'visibility_based'
        else:
            return 'default'
    
    def calculate_relative_x_position(self, obj: Dict[str, Any], 
                                    agent_position: Dict[str, Any]) -> float:
        """Calculate relative X position of object to agent.
        
        Args:
            obj: Object dictionary
            agent_position: Agent position
            
        Returns:
            Relative X position
        """
        obj_pos = obj.get('position', {})
        agent_pos = agent_position
        
        # Calculate relative position considering agent's rotation
        dx = obj_pos.get('x', 0) - agent_pos.get('x', 0)
        dz = obj_pos.get('z', 0) - agent_pos.get('z', 0)
        
        # Get agent's rotation
        agent_rotation = agent_pos.get('rotation', {}).get('y', 0)
        
        # Transform to agent's coordinate system
        cos_rot = math.cos(math.radians(agent_rotation))
        sin_rot = math.sin(math.radians(agent_rotation))
        
        # Relative X position (left-right from agent's perspective)
        relative_x = dx * cos_rot + dz * sin_rot
        
        return relative_x
    
    def calculate_distance(self, pos1: Dict[str, Any], pos2: Dict[str, Any]) -> float:
        """Calculate Euclidean distance between two positions.
        
        Args:
            pos1: First position
            pos2: Second position
            
        Returns:
            Euclidean distance
        """
        dx = pos1.get('x', 0) - pos2.get('x', 0)
        dz = pos1.get('z', 0) - pos2.get('z', 0)
        return math.sqrt(dx * dx + dz * dz)


class EnhancedAmbiguityResolver:
    """Enhanced ambiguity resolver with VLM numbered response support."""
    
    def __init__(self, vlm_response_parser: VLMResponseParser = None):
        """Initialize the resolver.
        
        Args:
            vlm_response_parser: VLM response parser instance
        """
        self.response_parser = vlm_response_parser or VLMResponseParser()
        self.object_sorter = SmartObjectSorting()
    
    def resolve_object_reference(self, instruction: str, candidate_objects: List[Dict[str, Any]], 
                               vlm_response: str, agent_position: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Resolve object reference using VLM response.
        
        Args:
            instruction: Original instruction
            candidate_objects: List of candidate objects
            vlm_response: VLM response text
            agent_position: Optional agent position
            
        Returns:
            Dictionary with resolution result
        """
        # Check if VLM response contains numbered reference
        if self.response_parser.contains_numbered_reference(vlm_response):
            selected_object = self.response_parser.parse_numbered_response(
                vlm_response, candidate_objects
            )
            
            if selected_object:
                return {
                    'selected_object_id': selected_object.get('objectId'),
                    'selected_object': selected_object,
                    'confidence': 0.8,  # Numbered responses are usually reliable
                    'method': 'vlm_numbered_response',
                    'original_response': vlm_response,
                    'reasoning': f"VLM provided numbered reference: {vlm_response}"
                }
        
        # Fallback to spatial reasoning
        return self.fallback_to_spatial_reasoning(instruction, candidate_objects, agent_position)
    
    def fallback_to_spatial_reasoning(self, instruction: str, candidate_objects: List[Dict[str, Any]], 
                                    agent_position: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fallback to spatial reasoning when numbered parsing fails.
        
        Args:
            instruction: Original instruction
            candidate_objects: List of candidate objects
            agent_position: Optional agent position
            
        Returns:
            Dictionary with resolution result
        """
        if not candidate_objects:
            return {
                'selected_object_id': None,
                'selected_object': None,
                'confidence': 0.0,
                'method': 'fallback_failed',
                'reasoning': 'No candidate objects available'
            }
        
        # Get optimal sorting strategy
        strategy = self.object_sorter.get_optimal_sorting_strategy(instruction)
        
        # Sort objects using the selected strategy
        if strategy == 'distance_based' and agent_position:
            sorted_objects = self.object_sorter.sort_by_distance(candidate_objects, agent_position)
        elif strategy == 'visibility_based':
            sorted_objects = self.object_sorter.sort_by_visibility(candidate_objects)
        else:
            sorted_objects = self.object_sorter.sort_by_left_to_right(candidate_objects, agent_position)
        
        # Select the first object from sorted list
        selected_object = sorted_objects[0]
        
        return {
            'selected_object_id': selected_object.get('objectId'),
            'selected_object': selected_object,
            'confidence': 0.6,  # Lower confidence for fallback
            'method': f'spatial_fallback_{strategy}',
            'reasoning': f"Fallback using {strategy} strategy, selected first object"
        }