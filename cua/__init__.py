"""
Cursor UI Agent (CUA) - Automated visual interaction with Cursor IDE

Main Components:
- CursorUIAgent: Main orchestrator class
- VisualDetector: Computer vision for UI element detection  
- AutomationController: Mouse/keyboard automation
- HarnessIntegrator: Integration with existing harness system
"""

from .cursor_ui_agent import CursorUIAgent
from .integration.harness_integration import HarnessIntegrator, create_harness_integrator
from .config.settings import CUAConfig

__version__ = "1.0.0"
__author__ = "Actuarial AI Team"

# Main classes for external use
__all__ = [
    "CursorUIAgent",
    "HarnessIntegrator", 
    "create_harness_integrator",
    "CUAConfig"
]