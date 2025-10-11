from pathlib import Path
from test_framework.method_config import MethodConfig, StepConfig
from methods.friedland_xyz_bf_method import steps, validation, integration


def get_config() -> MethodConfig:
    """Get the configuration for the Friedland XYZ Bornhuetter-Ferguson Method."""
    project_root = Path(__file__).parent.parent.parent
    test_data_dir = project_root / "test_data" / "friedland_xyz_bf_method"
    ground_truth_path = test_data_dir / "ground_truth.json"
    
    config = MethodConfig(
        method_name="friedland_xyz_bf_method",
        display_name="Friedland XYZ Bornhuetter-Ferguson Method",
        test_data_dir=test_data_dir,
        ground_truth_path=ground_truth_path,
    )
    
    ground_truth = config.load_ground_truth()
    
    config.steps = [
        StepConfig(
            step_id="step_1",
            description="Calculate BF ultimates using latest-2 volume weighted LDFs with 1.05 tail",
            prompt_generator=steps.get_step_1_prompt,
            validator=lambda workspace_dir: validation.validate_step_1(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_2",
            description="Extract BF IBNR from model",
            prompt_generator=steps.get_step_2_prompt,
            validator=lambda workspace_dir: validation.validate_step_2(workspace_dir, ground_truth)
        ),
    ]
    
    config.integration_prompt_generator = integration.generate_integration_prompt
    config.integration_validator = lambda workspace_dir: integration.validate_integration(workspace_dir, ground_truth)
    
    return config

