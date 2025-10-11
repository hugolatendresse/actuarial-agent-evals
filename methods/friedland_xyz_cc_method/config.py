from pathlib import Path
from test_framework.method_config import MethodConfig, StepConfig
from methods.friedland_xyz_cc_method import steps, validation, integration


def get_config() -> MethodConfig:
    """Get the configuration for the Friedland XYZ Cape Cod Method."""
    project_root = Path(__file__).parent.parent.parent
    test_data_dir = project_root / "test_data" / "friedland_xyz_cc_method"
    ground_truth_path = test_data_dir / "ground_truth.json"
    
    config = MethodConfig(
        method_name="friedland_xyz_cc_method",
        display_name="Friedland XYZ Cape Cod Method",
        test_data_dir=test_data_dir,
        ground_truth_path=ground_truth_path,
    )
    
    ground_truth = config.load_ground_truth()
    
    config.steps = [
        StepConfig(
            step_id="step_1",
            description="Calculate current level earned premium using rate changes",
            prompt_generator=steps.get_step_1_prompt,
            validator=lambda workspace_dir: validation.validate_step_1(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_2",
            description="Calculate tort reform on-level factors",
            prompt_generator=steps.get_step_2_prompt,
            validator=lambda workspace_dir: validation.validate_step_2(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_3",
            description="Calculate adjusted reported claims for tort reform",
            prompt_generator=steps.get_step_3_prompt,
            validator=lambda workspace_dir: validation.validate_step_3(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_4",
            description="Calculate Cape Cod ultimate claims",
            prompt_generator=steps.get_step_4_prompt,
            validator=lambda workspace_dir: validation.validate_step_4(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_5",
            description="Calculate Cape Cod IBNR",
            prompt_generator=steps.get_step_5_prompt,
            validator=lambda workspace_dir: validation.validate_step_5(workspace_dir, ground_truth)
        ),
    ]
    
    config.integration_prompt_generator = integration.generate_integration_prompt
    config.integration_validator = lambda workspace_dir: integration.validate_integration(workspace_dir, ground_truth)
    
    return config

