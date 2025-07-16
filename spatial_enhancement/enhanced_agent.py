"""EnhancedRocAgent that integrates spatial reasoning capabilities."""

import sys
import os
import math
from typing import Dict, List, Any, Optional, Tuple

# Add paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from evaluate.ai2thor_engine.RocAgent import RocAgent
    from evaluate.ai2thor_engine.baseAgent import BaseAgent
except ImportError:
    # Fallback for development
    class RocAgent:
        def __init__(self, *args, **kwargs):
            pass
        def navigate(self, itemtype, itemname=None):
            return None, None, None
    
    class BaseAgent:
        def __init__(self, *args, **kwargs):
            pass

from .spatial_calculator import SpatialRelationCalculator
from .heuristic_detector import HeuristicAmbiguityDetector, AmbiguityResult
from .geometric_analyzer import GeometricAnalyzer, ObservationStrategy
from .vlm_response_parser import VLMResponseParser, EnhancedAmbiguityResolver

class EnhancedRocAgent(RocAgent):
    """Enhanced RocAgent with advanced spatial reasoning capabilities."""
    
    def __init__(self, controller, save_path="./data/", scene="FloorPlan203", 
                 visibilityDistance=1.5, gridSize=0.25, fieldOfView=90, 
                 target_objects=[], related_objects=[], navigable_objects=[], 
                 taskid=0, platform_type="GPU", enable_enhancements=True):
        """Initialize enhanced agent with spatial reasoning modules.
        
        Args:
            enable_enhancements: Whether to enable spatial enhancements
            Other args: Same as parent RocAgent
        """
        # Initialize parent class
        super().__init__(
            controller=controller,
            save_path=save_path,
            scene=scene,
            visibilityDistance=visibilityDistance,
            gridSize=gridSize,
            fieldOfView=fieldOfView,
            target_objects=target_objects,
            related_objects=related_objects,
            navigable_objects=navigable_objects,
            taskid=taskid,
            platform_type=platform_type
        )
        
        # Enhancement control
        self.enable_enhancements = enable_enhancements
        self.enhancement_stats = {
            'ambiguity_resolutions': 0,
            'spatial_calculations': 0,
            'geometric_optimizations': 0,
            'fallback_uses': 0
        }
        
        if self.enable_enhancements:
            # Initialize enhancement modules
            try:
                self.spatial_calculator = SpatialRelationCalculator(self.eventobject)
                self.ambiguity_detector = HeuristicAmbiguityDetector(self.spatial_calculator)
                self.geometric_analyzer = GeometricAnalyzer()
                self.vlm_response_parser = VLMResponseParser()
                self.enhanced_ambiguity_resolver = EnhancedAmbiguityResolver(self.vlm_response_parser)
                self.enhancements_available = True
                print("[Spatial Enhancement] Spatial enhancement modules loaded successfully")
            except Exception as e:
                print(f"[Spatial Enhancement] Failed to load enhancement modules: {e}")
                self.enhancements_available = False
                self.enable_enhancements = False
        else:
            self.enhancements_available = False
    
    def navigate(self, itemtype: str, itemname: Optional[str] = None) -> Tuple[Any, Any, Any]:
        """Enhanced navigation with ambiguity resolution.
        
        Args:
            itemtype: Type of object to navigate to
            itemname: Optional specific name/description
            
        Returns:
            Tuple of (image_fp, legal_navigations, legal_interactions)
        """
        if not self.enable_enhancements or not self.enhancements_available:   # Use original navigation
            return super().navigate(itemtype)
        
        try:
            # Get candidate objects of the specified type
            candidates = self._get_candidate_objects(itemtype)
            
            if len(candidates) <= 1: # which means there's no ambiguity, just use the original method
                return super().navigate(itemtype)
            
            # enhanced disambiguation
            self.enhancement_stats['ambiguity_resolutions'] += 1
            
            # Use itemname if provided, otherwise use itemtype
            instruction = itemname if itemname else f"navigate to {itemtype}"  # Futher TODO: add more instructions
            
            # Detect and resolve ambiguity
            ambiguity_result = self.ambiguity_detector.detect_ambiguity(instruction, candidates)
            
            if ambiguity_result.selected_object_id and ambiguity_result.confidence > 0.5:
                selected_object = next(
                    (obj for obj in candidates if obj.get('objectId') == ambiguity_result.selected_object_id),
                    None
                )
                
                if selected_object:
                    return self._navigate_to_specific_object(selected_object, itemtype)
            
            self.enhancement_stats['fallback_uses'] += 1
            if ambiguity_result.clarification_question:
                print(f"[Spatial Enhancement] Ambiguity detected: {ambiguity_result.clarification_question}")
                # use the closest object as fallback
                relations = self.spatial_calculator.calculate_relative_positions(candidates)
                closest_obj_id = min(relations.items(), key=lambda x: x[1].distance_to_agent)[0]
                selected_object = next(
                    (obj for obj in candidates if obj.get('objectId') == closest_obj_id),
                    None
                )
                if selected_object:
                    return self._navigate_to_specific_object(selected_object, itemtype)
            
            # Final fallback, only rely on the original, first-order method
            return super().navigate(itemtype)
            
        except Exception as e:
            print(f"[Spatial Enhancement] Enhancement navigation failed: {e}")
            self.enhancement_stats['fallback_uses'] += 1 # increase the negative metric that measures the effectiveness of the enhancement
            return super().navigate(itemtype)
    
    def _get_candidate_objects(self, itemtype: str) -> List[Dict[str, Any]]:
        """Get all objects of the specified type.
        
        Args:
            itemtype: Object type to search for
            
        Returns:
            List of candidate objects
        """
        candidates = []
        
        # Check target objects first
        if itemtype in self.target_item_type2obj_id:
            for obj_id in self.target_item_type2obj_id[itemtype]:
                try:
                    obj = self.eventobject.get_object_by_id(self.controller.last_event, obj_id)
                    if obj:
                        candidates.append(obj)
                except:
                    pass
        
        # Also, the general object types
        if itemtype in self.objecttype2object:
            candidates.extend(self.objecttype2object[itemtype])
        
        # Remove duplicates based on objectId
        unique_candidates = []
        seen_ids = set()
        for obj in candidates:
            obj_id = obj.get('objectId')
            if obj_id and obj_id not in seen_ids:
                unique_candidates.append(obj)
                seen_ids.add(obj_id)
        
        return unique_candidates
    
    def _navigate_to_specific_object(self, target_object: Dict[str, Any], 
                                   itemtype: str) -> Tuple[Any, Any, Any]:
        """Navigate to a specific object using enhanced positioning.
        
        Args:
            target_object: The specific object to navigate to
            itemtype: Object type for compatibility
            
        Returns:
            Tuple of (image_fp, legal_navigations, legal_interactions)
        """
        try:
            # Use geometric analyzer for better positioning
            if hasattr(self, 'geometric_analyzer'):
                self.enhancement_stats['geometric_optimizations'] += 1
                
                # Get enhanced positioning strategy
                positions = self._compute_enhanced_position(target_object)
                
                if positions:
                    return self._execute_navigation_to_position(target_object, positions[0], itemtype)
            
            # Fallback to original positioning
            return self._execute_original_navigation(target_object, itemtype)
            
        except Exception as e:
            print(f"[Spatial Enhancement] Enhanced positioning failed: {e}")
            return self._execute_original_navigation(target_object, itemtype)
    
    def _compute_enhanced_position(self, target_object: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compute enhanced positions using geometric analysis.
        
        Args:
            target_object: Object to navigate to
            
        Returns:
            List of optimal positions
        """
        try:
            # Get all reachable positions (similar to compute_position_8)
            event = self.controller.step(dict(action='GetInteractablePoses', 
                                            objectId=target_object['objectId']))
            reachable_positions = event.metadata['actionReturn']
            
            if not reachable_positions:
                return []
            
            # Use geometric analyzer to filter and rank positions
            enhanced_positions = self.geometric_analyzer.get_enhanced_positioning_strategy(
                target_object, reachable_positions
            )
            
            return enhanced_positions
            
        except Exception as e:
            print(f"Enhanced position computation failed: {e}")
            return []
    
    def _execute_navigation_to_position(self, target_object: Dict[str, Any], 
                                      position: Dict[str, Any], 
                                      itemtype: str) -> Tuple[Any, Any, Any]:
        """Execute navigation to a specific position.
        
        Args:
            target_object: Target object
            position: Position to navigate to
            itemtype: Object type for compatibility
            
        Returns:
            Tuple of (image_fp, legal_navigations, legal_interactions)
        """
        # Calculate rotation to face the object
        obj_pos = target_object.get('position', {})
        dx = obj_pos.get('x', 0) - position.get('x', 0)
        dz = obj_pos.get('z', 0) - position.get('z', 0)
        
        # Calculate angle to face object
        angle = math.degrees(math.atan2(dx, dz))
        if angle < 0:
            angle += 360
        
        target_rotation = {'x': 0, 'y': angle, 'z': 0}
        horizon = 60  # Default horizon
        
        # Teleport to position
        event = self.action.action_mapping["teleport"](
            self.controller, 
            position=position, 
            rotation=target_rotation, 
            horizon=horizon
        )
        
        if not event.metadata['lastActionSuccess']:
            # Retry with original method if teleport fails
            return self._execute_original_navigation(target_object, itemtype)
        
        # Adjust view and height if needed
        self.adjust_height(target_object)
        self.adjust_view(target_object)
        
        # Save frame and return
        image_fp = self.save_frame({
            "step_count": str(self.step_count),
            "action": "navigate_enhanced",
            "item": itemtype
        }, prefix_save_path=self.result_dir)
        
        # Update container if needed
        if target_object.get("receptacle", False) and target_object.get('receptacleObjectIds'):
            self.current_container = target_object
        
        legal_navigations = self.get_legal_navigations()
        legal_interactions = self.get_legal_interactions()
        
        return image_fp, legal_navigations, legal_interactions
    
    def _execute_original_navigation(self, target_object: Dict[str, Any], 
                                   itemtype: str) -> Tuple[Any, Any, Any]:
        """Execute navigation using original RocAgent method.
        
        Args:
            target_object: Target object
            itemtype: Object type
            
        Returns:
            Tuple of (image_fp, legal_navigations, legal_interactions)
        """
        # Temporarily modify target_item_type2obj_id to point to specific object
        original_mapping = self.target_item_type2obj_id.get(itemtype, [])
        self.target_item_type2obj_id[itemtype] = [target_object.get('objectId')]
        
        try:
            result = super().navigate(itemtype)
            return result
        finally:
            # Restore original mapping
            if original_mapping:
                self.target_item_type2obj_id[itemtype] = original_mapping
            elif itemtype in self.target_item_type2obj_id:
                del self.target_item_type2obj_id[itemtype]
    
    def get_enhancement_stats(self) -> Dict[str, Any]:
        """Get statistics about enhancement usage.
        
        Returns:
            Dictionary with enhancement statistics
        """
        return {
            'enhancements_enabled': self.enable_enhancements,
            'enhancements_available': self.enhancements_available,
            'stats': self.enhancement_stats.copy()
        }
    
    def toggle_enhancements(self, enabled: bool):
        """Enable or disable spatial enhancements.
        
        Args:
            enabled: Whether to enable enhancements
        """
        if enabled and not self.enhancements_available:
            print("[Spatial Enhancement] Cannot enable enhancements: modules not available")
            return False
        
        self.enable_enhancements = enabled
        return True
    
    def reset_enhancement_stats(self):
        """Reset enhancement usage statistics."""
        self.enhancement_stats = {
            'ambiguity_resolutions': 0,
            'spatial_calculations': 0,
            'geometric_optimizations': 0,
            'fallback_uses': 0
        }
    
    def resolve_vlm_response(self, vlm_response: str, candidate_objects: List[Dict[str, Any]], 
                           instruction: str = "") -> Optional[Dict[str, Any]]:
        """Resolve VLM response that may contain numbered object references.
        
        Args:
            vlm_response: The VLM response text
            candidate_objects: List of candidate objects
            instruction: Original instruction for context
            
        Returns:
            Selected object or None if resolution fails
        """
        if not self.enable_enhancements or not self.enhancements_available:
            return None
        
        try:
            # Get agent position for spatial reasoning
            agent_position = None
            if hasattr(self, 'controller') and self.controller:
                event = self.controller.last_event
                if event and event.metadata:
                    agent_position = event.metadata.get('agent', {}).get('position', {})
            
            # Use enhanced ambiguity resolver
            result = self.enhanced_ambiguity_resolver.resolve_object_reference(
                instruction, candidate_objects, vlm_response, agent_position
            )
            
            if result.get('selected_object_id'):
                print(f"[Spatial Enhancement] VLM response resolved: {result['method']} - {result['reasoning']}")
                return result.get('selected_object')
            
            return None
            
        except Exception as e:
            print(f"[Spatial Enhancement] VLM response resolution failed: {e}")
            return None
    
    def navigate_with_vlm_response(self, itemtype: str, vlm_response: str, 
                                 instruction: str = "") -> Tuple[Any, Any, Any]:
        """Navigate using VLM response that may contain numbered references.
        
        Args:
            itemtype: Type of object to navigate to
            vlm_response: VLM response text
            instruction: Original instruction for context
            
        Returns:
            Tuple of (image_fp, legal_navigations, legal_interactions)
        """
        if not self.enable_enhancements or not self.enhancements_available:
            return super().navigate(itemtype)
        
        try:
            # Get candidate objects
            candidates = self._get_candidate_objects(itemtype)
            
            if len(candidates) <= 1:
                return super().navigate(itemtype)
            
            # Try to resolve VLM response
            selected_object = self.resolve_vlm_response(vlm_response, candidates, instruction)
            
            if selected_object:
                return self._navigate_to_specific_object(selected_object, itemtype)
            
            # Fallback to original navigation
            return super().navigate(itemtype)
            
        except Exception as e:
            print(f"[Spatial Enhancement] VLM navigation failed: {e}")
            return super().navigate(itemtype)

# Compatibility wrapper for easy replacement
class LightweightEnhancementAdapter:
    """Lightweight adapter for easy integration with existing code."""
    
    def __init__(self, original_agent_class):
        """Initialize with original agent class.
        
        Args:
            original_agent_class: Original RocAgent class
        """
        self.original_agent_class = original_agent_class
    
    def create_agent(self, *args, **kwargs):
        """Create enhanced or original agent based on configuration.
        
        Returns:
            Enhanced agent if available, otherwise original agent
        """
        enable_enhancements = kwargs.pop('enable_enhancements', True)
        
        if enable_enhancements:
            try:
                return EnhancedRocAgent(*args, **kwargs, enable_enhancements=True)
            except Exception as e:
                print(f"Failed to create enhanced agent: {e}")
                print("Falling back to original agent")
        
        # Fallback to original agent
        return self.original_agent_class(*args, **kwargs)