#!/usr/bin/env python3
"""Test script for VLM response parser functionality."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'spatial_enhancement'))

from spatial_enhancement.vlm_response_parser import VLMResponseParser, EnhancedAmbiguityResolver

def test_vlm_response_parser():
    """Test VLM response parser with sample data."""
    print("=== Testing VLM Response Parser ===")
    
    # Initialize parser
    parser = VLMResponseParser()
    
    # Sample candidate objects (simulating two vases)
    candidate_objects = [
        {
            'objectId': 'Vase_1',
            'objectType': 'Vase', 
            'position': {'x': 1.0, 'y': 0.5, 'z': 2.0},
            'visible': True
        },
        {
            'objectId': 'Vase_2',
            'objectType': 'Vase',
            'position': {'x': 3.0, 'y': 0.5, 'z': 2.0},
            'visible': True
        }
    ]
    
    # Test cases
    test_cases = [
        "navigate to vase1",
        "navigate to vase2", 
        "pick up vase1",
        "go to vase2",
        "vase1",
        "vase2",
        "navigate to vase",  # No number
        "navigate to apple1",  # Wrong type
        "navigate to vase5"   # Number too high
    ]
    
    print("\nTesting VLM response parsing:")
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: '{test_case}'")
        result = parser.parse_numbered_response(test_case, candidate_objects)
        if result:
            print(f"  ✅ Selected: {result['objectId']} at position {result['position']}")
        else:
            print(f"  ❌ No match found")
    
    # Test contains_numbered_reference
    print("\nTesting numbered reference detection:")
    for test_case in test_cases:
        has_number = parser.contains_numbered_reference(test_case)
        print(f"  '{test_case}': {has_number}")
    
    # Test enhanced ambiguity resolver
    print("\n=== Testing Enhanced Ambiguity Resolver ===")
    resolver = EnhancedAmbiguityResolver(parser)
    
    # Test with VLM response
    vlm_response = "navigate to vase1"
    instruction = "Can you grab the Vase from the room?"
    
    result = resolver.resolve_object_reference(instruction, candidate_objects, vlm_response)
    print(f"\nVLM Response: '{vlm_response}'")
    print(f"Result: {result}")
    
    # Test fallback
    vlm_response_no_number = "navigate to vase"
    result_fallback = resolver.resolve_object_reference(instruction, candidate_objects, vlm_response_no_number)
    print(f"\nFallback Response: '{vlm_response_no_number}'")
    print(f"Fallback Result: {result_fallback}")

if __name__ == "__main__":
    test_vlm_response_parser()