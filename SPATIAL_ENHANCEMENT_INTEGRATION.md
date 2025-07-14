# Spatial Enhancement Integration Guide

## Overview

The spatial enhancement modules have been integrated into the main Embodied-Reasoner project. This guide explains how to use the enhanced functionality.

## Quick Start

### Option 1: Use Enhanced Evaluation Script
```bash
# Use the enhanced evaluation script instead of the original
python evaluate/evaluate_enhanced.py
```

### Option 2: Import Enhanced Agent Directly
```python
from evaluate.ai2thor_engine.EnhancedRocAgent import EnhancedRocAgent

# Create enhanced agent (same parameters as original RocAgent)
agent = EnhancedRocAgent(
    controller=controller,
    scene="FloorPlan1",
    enable_spatial_enhancements=True  # New parameter
)

# Use exactly like original RocAgent
image, nav, interact = agent.navigate("Book")

# Check enhancement statistics
stats = agent.get_enhancement_stats()
print(f"Enhancements used: {stats}")
```

## Integration Points

### 1. Enhanced Navigation
- Automatically detects multiple objects of same type
- Resolves ambiguity using spatial reasoning
- Falls back to original behavior if enhancements fail

### 2. Improved Observation
- Dynamic distance calculation based on object geometry
- Multi-view strategies for large objects
- Single-view optimization for small objects

### 3. Bilingual Support
- Handles Chinese spatial instructions: "左边的书", "桌上的杯子"
- English spatial instructions: "left book", "cup on table"

## Configuration

### Enable/Disable Enhancements
```python
# Enable enhancements (default)
agent = EnhancedRocAgent(controller, enable_spatial_enhancements=True)

# Disable enhancements (use original behavior)
agent = EnhancedRocAgent(controller, enable_spatial_enhancements=False)

# Toggle at runtime
agent.toggle_enhancements(False)  # Disable
agent.toggle_enhancements(True)   # Enable
```

### Check Enhancement Status
```python
stats = agent.get_enhancement_stats()
print(f"Enhancements enabled: {stats['enhancements_enabled']}")
print(f"Modules available: {stats['enhancements_available']}")
print(f"Usage stats: {stats['stats']}")
```

## Testing

### Run Integration Tests
```bash
# Test with real AI2-THOR environment
python test_real_integration.py

# Test standalone modules
python test_spatial_enhancement.py
```

## Backward Compatibility

The enhanced agent maintains full backward compatibility:
- Same constructor parameters as original RocAgent
- Same method signatures
- Same return values
- Graceful fallback to original behavior

## File Structure

```
evaluate/ai2thor_engine/
├── RocAgent.py                    # Original agent
├── EnhancedRocAgent.py           # Enhanced wrapper
└── spatial_enhancement/          # Enhancement modules
    ├── __init__.py
    ├── spatial_calculator.py
    ├── heuristic_detector.py
    ├── geometric_analyzer.py
    ├── enhanced_agent.py
    └── test_framework.py

evaluate/
├── evaluate.py                   # Original evaluation
└── evaluate_enhanced.py          # Enhanced evaluation
```

## Troubleshooting

### Import Errors
If you see import errors, ensure the spatial_enhancement modules are in the correct location:
```bash
ls evaluate/ai2thor_engine/spatial_enhancement/
```

### Enhancement Not Working
Check enhancement status:
```python
print(agent.get_enhancement_stats())
```

### Performance Issues
Monitor enhancement statistics:
```python
stats = agent.get_enhancement_stats()
print(f"Fallback uses: {stats['stats']['fallback_uses']}")
```

## Performance Metrics

The enhanced agent tracks usage statistics:
- `ambiguity_resolutions`: Number of ambiguous cases resolved
- `spatial_calculations`: Spatial reasoning operations performed
- `geometric_optimizations`: Geometric analysis optimizations used
- `fallback_uses`: Times fallback to original behavior was needed

Lower `fallback_uses` indicates better enhancement effectiveness.
