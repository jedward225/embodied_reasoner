"""Enhanced RocAgent wrapper for seamless integration."""

import sys
import os
from pathlib import Path

# Add parent directories to path to find spatial_enhancement
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent  # Go up to embodied_reasoner
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

try:
    from .RocAgent import RocAgent as OriginalRocAgent
    # Import from project root
    from spatial_enhancement.enhanced_agent import EnhancedRocAgent as ImportedEnhancedRocAgent
    
    # Use the imported enhanced agent directly
    EnhancedRocAgent = ImportedEnhancedRocAgent
    
    print("[EnhancedRocAgent] Successfully loaded spatial enhancement modules")
    
    # Export both versions for backward compatibility
    __all__ = ['EnhancedRocAgent', 'OriginalRocAgent']
    
except ImportError as e:
    print(f"[EnhancedRocAgent] Warning: Could not import enhanced modules: {e}")
    print(f"[EnhancedRocAgent] Current dir: {current_dir}")
    print(f"[EnhancedRocAgent] Project root: {project_root if 'project_root' in locals() else 'Not set'}")
    # Fallback to original RocAgent
    from .RocAgent import RocAgent
    EnhancedRocAgent = RocAgent
    OriginalRocAgent = RocAgent
    
    __all__ = ['EnhancedRocAgent', 'OriginalRocAgent']
