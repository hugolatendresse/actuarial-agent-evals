from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Callable, List, Optional


@dataclass
class StepConfig:
    """Configuration for a single test step."""
    step_id: str
    description: str
    prompt_generator: Callable[[Dict[str, Any]], str]
    validator: Callable[[Path], Dict[str, Any]]


@dataclass
class MethodConfig:
    """Configuration for an actuarial method test."""
    method_name: str
    display_name: str
    test_data_dir: Path
    ground_truth_path: Path
    steps: List[StepConfig] = field(default_factory=list)
    integration_prompt_generator: Optional[Callable[[], str]] = None
    integration_validator: Optional[Callable[[Path], Dict[str, Any]]] = None
    
    def load_ground_truth(self) -> Dict[str, Any]:
        """Load ground truth data from JSON file."""
        import json
        with open(self.ground_truth_path, 'r') as f:
            return json.load(f)
    
    def get_data_files(self, pattern: str = "*.csv") -> List[Path]:
        """Get list of data files for the method."""
        return sorted(self.test_data_dir.glob(pattern))


class MethodRegistry:
    """Registry for actuarial method configurations."""
    
    _methods: Dict[str, MethodConfig] = {}
    
    @classmethod
    def register(cls, config: MethodConfig) -> None:
        """Register a method configuration."""
        cls._methods[config.method_name] = config
    
    @classmethod
    def get(cls, method_name: str) -> MethodConfig:
        """Get a method configuration by name."""
        if method_name not in cls._methods:
            raise ValueError(f"Method '{method_name}' not found in registry. Available: {list(cls._methods.keys())}")
        return cls._methods[method_name]
    
    @classmethod
    def list_methods(cls) -> List[str]:
        """List all registered method names."""
        return list(cls._methods.keys())
    
    @classmethod
    def discover_methods(cls) -> None:
        """Discover and register methods from the methods directory."""
        methods_dir = Path(__file__).parent.parent / "methods"
        if not methods_dir.exists():
            return
        
        for method_path in methods_dir.iterdir():
            if method_path.is_dir() and not method_path.name.startswith('_'):
                config_file = method_path / "config.py"
                if config_file.exists():
                    try:
                        import importlib.util
                        spec = importlib.util.spec_from_file_location(
                            f"methods.{method_path.name}.config",
                            config_file
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        if hasattr(module, 'get_config'):
                            config = module.get_config()
                            cls.register(config)
                    except Exception as e:
                        print(f"Warning: Could not load method config from {config_file}: {e}")

