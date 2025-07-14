"""HeuristicAmbiguityDetector for detecting and resolving object ambiguity using heuristic rules."""

import re
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from .spatial_calculator import SpatialRelationCalculator

@dataclass
class AmbiguityResult:
    """Result of ambiguity detection and resolution."""
    has_ambiguity: bool
    reason: str
    selected_object_id: Optional[str] = None
    confidence: float = 0.0
    clarification_question: Optional[str] = None
    alternative_objects: List[str] = None

class HeuristicAmbiguityDetector:
    """Detects and resolves object ambiguity using heuristic rules."""
    
    def __init__(self, spatial_calculator: Optional[SpatialRelationCalculator] = None):
        """Initialize with optional spatial calculator.
        
        Args:
            spatial_calculator: For calculating spatial relationships
        """
        self.spatial_calculator = spatial_calculator
        
        # Spatial relationship patterns
        self.spatial_patterns = {
            'directional': [
                r'(左|左边|left|左侧)',
                r'(右|右边|right|右侧)', 
                r'(前|前面|front|ahead|前方)',
                r'(后|后面|back|behind|后方)'
            ],
            'proximity': [
                r'(靠近|附近|near|close|nearby)',
                r'(远|远离|far|distant)',
                r'(旁边|beside|next to)',
                r'(之间|between)'
            ],
            'landmark': [
                r'(窗户|window).*?(旁|边|附近|near)',
                r'(门|door).*?(旁|边|附近|near)',
                r'(墙|wall).*?(旁|边|附近|near)'
            ],
            'container': [
                r'(桌|table).*?(上|on)',
                r'(架|shelf).*?(上|on|里|in)',
                r'(柜|cabinet).*?(里|in)',
                r'(抽屉|drawer).*?(里|in)'
            ]
        }
        
        # Object type synonyms for better matching
        self.object_synonyms = {
            'book': ['书', '书本', 'book'],
            'cup': ['杯子', '茶杯', 'cup', 'mug'],
            'apple': ['苹果', 'apple'],
            'remote': ['遥控器', 'remote', 'controller'],
            'pillow': ['枕头', 'pillow', 'cushion'],
            'knife': ['刀', 'knife'],
            'plate': ['盘子', '盘', 'plate', 'dish']
        }
    
    def detect_ambiguity(self, instruction: str, candidate_objects: List[Dict[str, Any]]) -> AmbiguityResult:
        """Detect if instruction contains ambiguous object references.
        
        Args:
            instruction: Natural language instruction
            candidate_objects: List of objects with same type
            
        Returns:
            AmbiguityResult with detection outcome
        """
        if len(candidate_objects) <= 1:
            return AmbiguityResult(
                has_ambiguity=False,
                reason="Only one candidate object available"
            )
        
        # Check for spatial keywords in instruction
        spatial_keywords = self._extract_spatial_keywords(instruction)
        
        if spatial_keywords:
            # Has spatial constraints, try to resolve
            if self.spatial_calculator:
                best_match, confidence = self.spatial_calculator.find_best_spatial_match(
                    candidate_objects, instruction
                )
                
                if confidence > 0.7:
                    return AmbiguityResult(
                        has_ambiguity=False,
                        reason="Resolved using spatial constraints",
                        selected_object_id=best_match,
                        confidence=confidence
                    )
                elif confidence > 0.4:
                    return AmbiguityResult(
                        has_ambiguity=True,
                        reason="Low confidence in spatial resolution",
                        selected_object_id=best_match,
                        confidence=confidence,
                        clarification_question=self._generate_clarification_question(
                            candidate_objects, spatial_keywords
                        )
                    )
                else:
                    return AmbiguityResult(
                        has_ambiguity=True,
                        reason="Cannot resolve spatial constraints",
                        clarification_question=self._generate_clarification_question(
                            candidate_objects, spatial_keywords
                        )
                    )
            else:
                return AmbiguityResult(
                    has_ambiguity=True,
                    reason="Spatial constraints detected but no spatial calculator available",
                    clarification_question=self._generate_clarification_question(
                        candidate_objects, spatial_keywords
                    )
                )
        else:
            # No spatial constraints, ambiguous
            return AmbiguityResult(
                has_ambiguity=True,
                reason="Multiple objects of same type, no spatial constraints",
                clarification_question=self._generate_simple_clarification(candidate_objects)
            )
    
    def _extract_spatial_keywords(self, instruction: str) -> Dict[str, List[str]]:
        """Extract spatial keywords from instruction.
        
        Args:
            instruction: Natural language instruction
            
        Returns:
            Dictionary with spatial pattern types and matched keywords
        """
        found_patterns = {}
        instruction_lower = instruction.lower()
        
        for pattern_type, patterns in self.spatial_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, instruction_lower, re.IGNORECASE)
                if found:
                    matches.extend(found)
            
            if matches:
                found_patterns[pattern_type] = matches
                
        return found_patterns
    
    def heuristic_object_selection(self, instruction: str, 
                                 candidate_objects: List[Dict[str, Any]]) -> AmbiguityResult:
        """Select object using heuristic rules.
        
        Args:
            instruction: Natural language instruction
            candidate_objects: List of candidate objects
            
        Returns:
            AmbiguityResult with selection outcome
        """
        if not candidate_objects:
            return AmbiguityResult(
                has_ambiguity=False,
                reason="No candidate objects"
            )
            
        if len(candidate_objects) == 1:
            return AmbiguityResult(
                has_ambiguity=False,
                reason="Single candidate object",
                selected_object_id=candidate_objects[0].get('objectId'),
                confidence=1.0
            )
        
        # Rule 1: Prefer visible objects
        visible_objects = [obj for obj in candidate_objects if obj.get('visible', True)]
        if len(visible_objects) == 1:
            return AmbiguityResult(
                has_ambiguity=False,
                reason="Only one visible object",
                selected_object_id=visible_objects[0].get('objectId'),
                confidence=0.8
            )
        
        # Rule 2: Use spatial relationships if available
        if self.spatial_calculator:
            spatial_keywords = self._extract_spatial_keywords(instruction)
            if spatial_keywords:
                best_match, confidence = self.spatial_calculator.find_best_spatial_match(
                    candidate_objects, instruction
                )
                if confidence > 0.5:
                    return AmbiguityResult(
                        has_ambiguity=False,
                        reason="Spatial heuristic selection",
                        selected_object_id=best_match,
                        confidence=confidence
                    )
        
        # Rule 3: Prefer closest object to agent
        if self.spatial_calculator:
            relations = self.spatial_calculator.calculate_relative_positions(candidate_objects)
            closest_obj = min(relations.items(), key=lambda x: x[1].distance_to_agent)
            
            return AmbiguityResult(
                has_ambiguity=True,
                reason="Multiple candidates, selected closest",
                selected_object_id=closest_obj[0],
                confidence=0.4,
                clarification_question=self._generate_simple_clarification(candidate_objects)
            )
        
        # Rule 4: Default to first object (fallback)
        return AmbiguityResult(
            has_ambiguity=True,
            reason="Multiple candidates, using default selection",
            selected_object_id=candidate_objects[0].get('objectId'),
            confidence=0.3,
            clarification_question=self._generate_simple_clarification(candidate_objects)
        )
    
    def _generate_clarification_question(self, candidates: List[Dict[str, Any]], 
                                       spatial_keywords: Dict[str, List[str]]) -> str:
        """Generate a clarification question based on spatial context.
        
        Args:
            candidates: List of candidate objects
            spatial_keywords: Extracted spatial keywords
            
        Returns:
            Clarification question string
        """
        object_type = candidates[0].get('objectType', 'object')
        count = len(candidates)
        
        # Build question based on spatial keywords found
        if 'directional' in spatial_keywords:
            return f"I found {count} {object_type}s. Could you specify which direction you mean (left, right, front, or back)?"
        elif 'proximity' in spatial_keywords:
            return f"I found {count} {object_type}s. Could you specify which one is closer to you or a landmark?"
        elif 'landmark' in spatial_keywords:
            return f"I found {count} {object_type}s. Could you clarify which landmark you're referring to?"
        elif 'container' in spatial_keywords:
            return f"I found {count} {object_type}s. Could you specify which container or surface?"
        else:
            return f"I found {count} {object_type}s. Could you help me identify which one you want?"
    
    def _generate_simple_clarification(self, candidates: List[Dict[str, Any]]) -> str:
        """Generate a simple clarification question.
        
        Args:
            candidates: List of candidate objects
            
        Returns:
            Clarification question string
        """
        object_type = candidates[0].get('objectType', 'object')
        count = len(candidates)
        
        # Try to provide location-based clarification if spatial calculator available
        if self.spatial_calculator and len(candidates) <= 3:
            relations = self.spatial_calculator.calculate_relative_positions(candidates)
            locations = []
            
            for obj_id, relation in relations.items():
                if relation.distance_to_agent < 2.0:
                    locations.append(f"one nearby ({relation.relative_direction})")
                else:
                    locations.append(f"one farther away ({relation.relative_direction})")
            
            if len(locations) == len(candidates):
                location_desc = " and ".join(locations)
                return f"I see {count} {object_type}s: {location_desc}. Which one would you like?"
        
        # Fallback to simple question
        return f"I found {count} {object_type}s in the scene. Could you provide more details about which one you want?"
    
    def set_spatial_calculator(self, spatial_calculator: SpatialRelationCalculator):
        """Set the spatial calculator for enhanced disambiguation.
        
        Args:
            spatial_calculator: SpatialRelationCalculator instance
        """
        self.spatial_calculator = spatial_calculator