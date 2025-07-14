"""Enhanced RocAgent wrapper for seamless integration."""

import sys
import os
from pathlib import Path

# Add spatial enhancement to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from .RocAgent import RocAgent as OriginalRocAgent
    from spatial_enhancement.enhanced_agent import EnhancedRocAgent as BaseEnhancedRocAgent
    
    class EnhancedRocAgent(BaseEnhancedRocAgent, OriginalRocAgent):
        """Enhanced RocAgent that properly inherits from the original."""
        
        def __init__(self, *args, **kwargs):
            # Extract enhancement flag
            enable_enhancements = kwargs.pop('enable_spatial_enhancements', True)
            
            # Initialize original RocAgent first
            OriginalRocAgent.__init__(self, *args, **kwargs)
            
            # Then initialize enhancements
            BaseEnhancedRocAgent.__init__(self, *args, **kwargs, enable_enhancements=enable_enhancements)
            
        def navigate(self, itemtype, itemname=None):
            """Override navigate to use enhanced functionality."""
            if hasattr(self, 'enable_enhancements') and self.enable_enhancements:
                return BaseEnhancedRocAgent.navigate(self, itemtype, itemname)
            else:
                return OriginalRocAgent.navigate(self, itemtype)
    
    # Export both versions for backward compatibility
    __all__ = ['EnhancedRocAgent', 'OriginalRocAgent']
    
except ImportError as e:
    print(f"Warning: Could not import enhanced modules: {e}")
    # Fallback to original RocAgent
    from .RocAgent import RocAgent as EnhancedRocAgent
    from .RocAgent import RocAgent as OriginalRocAgent
    
    __all__ = ['EnhancedRocAgent', 'OriginalRocAgent']
