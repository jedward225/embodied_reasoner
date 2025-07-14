# 🚀 Spatial Enhancement Integration Usage Guide

## ✅ Integration Status
The spatial enhancement modules have been successfully integrated into your main project! You can now use enhanced spatial reasoning in your existing evaluation pipeline.

## 🔧 How to Use Enhanced Evaluation

### Option 1: Use Enhanced Evaluation Script (Recommended)
```bash
# Instead of running:
python evaluate/evaluate.py

# Now run:
python evaluate/evaluate_enhanced.py
```

### Option 2: Modify Your Existing Code
Replace your RocAgent imports in your evaluation scripts:

```python
# OLD:
from evaluate.ai2thor_engine.RocAgent import RocAgent

# NEW:
from evaluate.ai2thor_engine.EnhancedRocAgent import EnhancedRocAgent as RocAgent
```

The enhanced agent maintains the exact same interface as the original, so no other code changes are needed!

## 🎯 What You Get

### 1. Automatic Ambiguity Resolution
When there are multiple objects of the same type:

```python
# If scene has 3 books, the enhanced agent will:
# - Detect the ambiguity
# - Try to resolve using spatial clues from instructions
# - Ask clarifying questions if needed
# - Fall back to closest object if no resolution possible

agent.navigate("Book", "拿起左边的书")  # Will find the leftmost book
agent.navigate("Book", "get the book on the table")  # Will find book on table
agent.navigate("Book")  # Will ask: "I see 3 books, which one?"
```

### 2. Smart Observation Strategies
The enhanced agent automatically chooses optimal observation distances and angles:

```python
# Small objects (cups, books): closer, single view
# Large objects (sofas, tables): farther, multiple views
# No code changes needed - happens automatically!
```

### 3. Bilingual Support
Works with both Chinese and English spatial instructions:

```python
agent.navigate("Book", "左边的书")      # Chinese
agent.navigate("Book", "left book")    # English
agent.navigate("Cup", "桌上的杯子")     # Chinese
agent.navigate("Cup", "cup on table") # English
```

## 📊 Monitoring Enhancement Usage

Check how well the enhancements are working:

```python
# Create enhanced agent
agent = EnhancedRocAgent(controller, scene="FloorPlan1")

# After running some navigation tasks
stats = agent.get_enhancement_stats()
print(f"Ambiguity resolutions: {stats['stats']['ambiguity_resolutions']}")
print(f"Spatial calculations: {stats['stats']['spatial_calculations']}")
print(f"Geometric optimizations: {stats['stats']['geometric_optimizations']}")
print(f"Fallback uses: {stats['stats']['fallback_uses']}")

# Lower fallback_uses means better enhancement effectiveness
```

## ⚙️ Configuration Options

### Enable/Disable Enhancements
```python
# Enable enhancements (default)
agent = EnhancedRocAgent(controller, enable_spatial_enhancements=True)

# Disable enhancements (pure original behavior)
agent = EnhancedRocAgent(controller, enable_spatial_enhancements=False)

# Toggle at runtime
agent.toggle_enhancements(False)  # Switch to original behavior
agent.toggle_enhancements(True)   # Switch back to enhanced
```

### Customizing Enhancement Parameters
```python
# Access and modify geometric analyzer settings
analyzer = agent.geometric_analyzer
config = analyzer.get_configuration()
print(f"Current config: {config}")

# Modify thresholds
new_config = {
    'small_object_volume_threshold': 0.15,  # Smaller threshold
    'large_object_volume_threshold': 1.2,   # Larger threshold
}
analyzer.update_configuration(new_config)
```

## 🧪 Testing Your Integration

### Quick Test
```python
from evaluate.ai2thor_engine.EnhancedRocAgent import EnhancedRocAgent
from ai2thor.controller import Controller

# Create controller and agent
controller = Controller(scene="FloorPlan1", headless=True)
agent = EnhancedRocAgent(controller, scene="FloorPlan1")

# Test navigation
result = agent.navigate("Book")
print(f"Navigation result: {result[0] is not None}")

# Check enhancement stats
stats = agent.get_enhancement_stats()
print(f"Enhancement stats: {stats}")
```

### Test with Your Existing Evaluation
1. Backup your current evaluation script
2. Modify it to use `EnhancedRocAgent` instead of `RocAgent`
3. Run your evaluation and compare results

## 📈 Expected Improvements

You should see improvements in:

1. **Success Rate**: Better object selection when multiple candidates exist
2. **Task Efficiency**: Fewer failed attempts due to wrong object selection
3. **User Experience**: Clearer feedback when disambiguation is needed
4. **Navigation Quality**: Better positioning for observation and interaction

## 🔍 Debugging

### If Enhancements Aren't Working
```python
# Check if enhancements are enabled and available
agent = EnhancedRocAgent(controller)
stats = agent.get_enhancement_stats()

if not stats['enhancements_enabled']:
    print("Enhancements are disabled")
    agent.toggle_enhancements(True)

if not stats['enhancements_available']:
    print("Enhancement modules failed to load")
    # Check import errors in console output
```

### Performance Issues
```python
# Monitor fallback usage
stats = agent.get_enhancement_stats()
fallback_rate = stats['stats']['fallback_uses'] / max(1, stats['stats']['ambiguity_resolutions'])

if fallback_rate > 0.3:  # More than 30% fallbacks
    print("High fallback rate - consider tuning parameters")
```

## 🔄 Migration Path

### Phase 1: Test Integration (Current)
- Use `evaluate_enhanced.py` for testing
- Keep original `evaluate.py` as backup
- Monitor enhancement statistics

### Phase 2: Gradual Adoption
- Modify specific evaluation scripts to use EnhancedRocAgent
- Compare results with original version
- Fine-tune parameters based on your specific scenarios

### Phase 3: Full Migration
- Replace all RocAgent usage with EnhancedRocAgent
- Remove backup scripts once confident
- Use enhancements as default behavior

## 🎉 You're Ready!

The spatial enhancement is now fully integrated into your project. Start by running:

```bash
python evaluate/evaluate_enhanced.py
```

And enjoy the improved spatial reasoning capabilities! 🧠✨