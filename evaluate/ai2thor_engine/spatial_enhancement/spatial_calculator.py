"""SpatialRelationCalculator for computing spatial relationships between objects and agent."""

import math
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import sys
import os

# Add parent directory to path to import spatial_perception
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from spatial_perception.basic_signature import SpatialSignature
except ImportError:
    # Fallback if spatial_perception is not available
    SpatialSignature = None

@dataclass
class SpatialRelation:
    """Represents spatial relationship between objects."""
    object_id: str
    distance_to_agent: float
    relative_direction: str  # "front", "back", "left", "right"    #, "up", "down"
    angle_to_agent: float    # in degrees
    is_visible: bool
    landmark_relations: Dict[str, str]  # e.g., {"window": "near", "door": "far"}
    container_relations: Dict[str, str]  # e.g., {"table": "on", "shelf": "in"}

class SpatialRelationCalculator:
    """Calculates spatial relationships between objects and agent."""
    
    def __init__(self, event_object=None):
        """Initialize with event object for accessing scene data.
        
        Args:
            event_object: AI2-THOR event object containing scene metadata
        """
        self.event_object = event_object
        self.direction_keywords = {
            'left': ['left', '左', '左边', '左侧'],
            'right': ['right', '右', '右边', '右侧'], 
            'front': ['front', 'ahead', '前', '前面', '前方'],
            'back': ['back', 'behind', '后', '后面', '后方'],
            # 'up': ['up', 'above', '上', '上面', '上方'],
            # 'down': ['down', 'under', 'bottom', '下', '下面', '下方'],
            'near': ['near', 'close', 'nearby', '靠近', '附近', '近'],
            'far': ['far', 'distant', '远', '远离', '远的']
        }
        
    def calculate_relative_positions(self, candidate_objects: List[Dict[str, Any]], 
                                   agent_position: Optional[Dict[str, float]] = None) -> Dict[str, SpatialRelation]:
        """Calculate spatial relations for a list of candidate objects.
        
        Args:
            candidate_objects: List of object metadata dictionaries
            agent_position: Current agent position (if None, gets from event_object)
            
        Returns:
            Dictionary mapping object_id to SpatialRelation
        """
        if agent_position is None and self.event_object:
            agent_position = self._get_agent_position()
        elif agent_position is None:
            # Default position if no event object
            agent_position = {'x': 0, 'y': 0, 'z': 0}
            
        relations = {}
        
        for obj in candidate_objects:
            obj_id = obj.get('objectId', obj.get('name', 'unknown'))
            obj_position = obj.get('position', {})
            
            # Calculate basic spatial metrics
            distance = self._calculate_distance(agent_position, obj_position)
            direction = self._calculate_relative_direction(agent_position, obj_position)
            angle = self._calculate_angle_to_object(agent_position, obj_position)
            is_visible = obj.get('visible', True)
            
            # Calculate landmark relations
            landmark_relations = self._calculate_landmark_relations(obj, candidate_objects)
            
            # Calculate container relations
            container_relations = self._calculate_container_relations(obj)
            
            relation = SpatialRelation(
                object_id=obj_id,
                distance_to_agent=distance,
                relative_direction=direction,
                angle_to_agent=angle,
                is_visible=is_visible,
                landmark_relations=landmark_relations,
                container_relations=container_relations
            )
            
            relations[obj_id] = relation
            
        return relations
    
    def _get_agent_position(self) -> Dict[str, float]:
        """Get current agent position from event object."""
        if hasattr(self.event_object, 'controller'):
            agent_meta = self.event_object.controller.last_event.metadata.get('agent', {})
            return agent_meta.get('position', {'x': 0, 'y': 0, 'z': 0})
        return {'x': 0, 'y': 0, 'z': 0}
        
    def _calculate_distance(self, pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
        """Calculate Euclidean distance between two positions."""
        return math.sqrt(
            (pos1.get('x', 0) - pos2.get('x', 0))**2 + 
            (pos1.get('z', 0) - pos2.get('z', 0))**2
        )
        
    def _calculate_relative_direction(self, agent_pos: Dict[str, float], 
                                    obj_pos: Dict[str, float]) -> str:
        """Calculate relative direction from agent to object."""
        dx = obj_pos.get('x', 0) - agent_pos.get('x', 0)
        dz = obj_pos.get('z', 0) - agent_pos.get('z', 0)
        
        # Calculate angle in radians, then convert to degrees
        angle = math.atan2(dx, dz)
        angle_deg = math.degrees(angle)
        
        # Normalize to 0-360 degrees
        if angle_deg < 0:
            angle_deg += 360
            
        # Map angle to direction
        if 315 <= angle_deg or angle_deg < 45:
            return "front"
        elif 45 <= angle_deg < 135:
            return "right"
        elif 135 <= angle_deg < 225:
            return "back"
        else:  # 225 <= angle_deg < 315
            return "left"
            
    def _calculate_angle_to_object(self, agent_pos: Dict[str, float], 
                                 obj_pos: Dict[str, float]) -> float:
        """Calculate angle from agent to object in degrees."""
        dx = obj_pos.get('x', 0) - agent_pos.get('x', 0)
        dz = obj_pos.get('z', 0) - agent_pos.get('z', 0)
        
        angle = math.atan2(dx, dz)
        angle_deg = math.degrees(angle)
        
        # Normalize to 0-360 degrees
        if angle_deg < 0:
            angle_deg += 360
            
        return angle_deg
        
    def _calculate_landmark_relations(self, obj: Dict[str, Any], 
                                    all_objects: List[Dict[str, Any]]) -> Dict[str, str]:
        """Calculate relations to scene landmarks (windows, doors, etc)."""
        landmark_types = ['Window', 'Door', 'DoorFrame', 'Wall']
        relations = {}
        
        obj_pos = obj.get('position', {})
        
        for other_obj in all_objects:
            if other_obj.get('objectType') in landmark_types:
                other_pos = other_obj.get('position', {})
                distance = self._calculate_distance(obj_pos, other_pos)
                
                landmark_type = other_obj.get('objectType', '').lower()
                if distance < 1.5:  # Close threshold
                    relations[landmark_type] = "near"
                elif distance > 3.0:  # Far threshold
                    relations[landmark_type] = "far"
                else:
                    relations[landmark_type] = "medium"
                    
        return relations
        
    def _calculate_container_relations(self, obj: Dict[str, Any]) -> Dict[str, str]:
        """Calculate containment relations (on table, in shelf, etc)."""
        relations = {}
        
        # Check if object is contained in another object
        parent_receptacles = obj.get('parentReceptacles', [])
        for receptacle in parent_receptacles:
            if '|' in receptacle:
                container_type = receptacle.split('|')[0].lower()
                relations[container_type] = "in" if "Cabinet" in receptacle or "Drawer" in receptacle else "on"
                
        return relations
        
    def extract_spatial_constraints(self, instruction: str) -> Dict[str, List[str]]:
        """Extract spatial keywords from natural language instruction.
        
        Args:
            instruction: Natural language instruction
            
        Returns:
            Dictionary with constraint types as keys and matched keywords as values
        """
        instruction_lower = instruction.lower()
        constraints = {}
        
        for direction_type, keywords in self.direction_keywords.items():
            matched = [kw for kw in keywords if kw in instruction_lower]
            if matched:
                constraints[direction_type] = matched
                
        return constraints
        
    def score_spatial_match(self, spatial_relation: SpatialRelation, 
                           spatial_constraints: Dict[str, List[str]]) -> float:
        """Score how well an object matches spatial constraints.
        
        Args:
            spatial_relation: Calculated spatial relation for object
            spatial_constraints: Extracted spatial constraints from instruction
            
        Returns:
            Match score between 0.0 and 1.0
        """
        if not spatial_constraints:
            return 0.5  # Neutral score if no constraints
            
        total_score = 0.0
        constraint_count = 0
        
        # Score directional constraints
        for direction_type, keywords in spatial_constraints.items():
            constraint_count += 1
            
            if direction_type in ['left', 'right', 'front', 'back']:
                if spatial_relation.relative_direction == direction_type:
                    total_score += 1.0
                else:
                    total_score += 0.0
                    
            elif direction_type == 'near':
                # Score based on distance (closer is better)
                if spatial_relation.distance_to_agent < 1.5:
                    total_score += 1.0
                elif spatial_relation.distance_to_agent < 3.0:
                    total_score += 0.5
                else:
                    total_score += 0.0
                    
            elif direction_type == 'far':
                # Score based on distance (farther is better)
                if spatial_relation.distance_to_agent > 3.0:
                    total_score += 1.0
                elif spatial_relation.distance_to_agent > 1.5:
                    total_score += 0.5
                else:
                    total_score += 0.0
                    
        # Bonus for visibility
        if spatial_relation.is_visible:
            total_score += 0.1
            
        # Normalize score
        if constraint_count > 0:
            return min(total_score / constraint_count, 1.0)
        else:
            return 0.5
            
    def find_best_spatial_match(self, candidates: List[Dict[str, Any]], 
                               instruction: str) -> Tuple[Optional[str], float]:
        """Find the best object that matches spatial constraints in instruction.
        
        Args:
            candidates: List of candidate objects
            instruction: Natural language instruction with spatial references
            
        Returns:
            Tuple of (best_object_id, confidence_score)
        """
        if not candidates:
            return None, 0.0
            
        # Extract spatial constraints from instruction
        constraints = self.extract_spatial_constraints(instruction)
        
        if not constraints:
            # No spatial constraints, return closest visible object
            relations = self.calculate_relative_positions(candidates)
            visible_objects = [(obj_id, rel) for obj_id, rel in relations.items() if rel.is_visible]
            
            if visible_objects:
                best_obj_id, best_rel = min(visible_objects, key=lambda x: x[1].distance_to_agent)
                return best_obj_id, 0.6  # Medium confidence
            else:
                # Return closest object even if not visible
                best_obj_id, best_rel = min(relations.items(), key=lambda x: x[1].distance_to_agent)
                return best_obj_id, 0.3  # Low confidence
                
        # Calculate spatial relations for all candidates
        relations = self.calculate_relative_positions(candidates)
        
        # Score each candidate against spatial constraints
        scored_candidates = []
        for obj_id, relation in relations.items():
            score = self.score_spatial_match(relation, constraints)
            scored_candidates.append((obj_id, score, relation))
            
        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        if scored_candidates:
            best_obj_id, best_score, best_relation = scored_candidates[0]
            
            # Adjust confidence based on score and visibility
            confidence = best_score
            if best_relation.is_visible:
                confidence = min(confidence + 0.1, 1.0)
                
            return best_obj_id, confidence
        else:
            return None, 0.0