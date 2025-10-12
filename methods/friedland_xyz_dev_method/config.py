from pathlib import Path
from test_framework.method_config import MethodConfig, StepConfig
from methods.friedland_xyz_dev_method import steps, validation, integration


def get_config() -> MethodConfig:
    """Get the configuration for the Friedland XYZ Development Method."""
    project_root = Path(__file__).parent.parent.parent
    test_data_dir = project_root / "test_data" / "friedland_xyz_dev_method"
    ground_truth_path = test_data_dir / "ground_truth.json"
    
    config = MethodConfig(
        method_name="friedland_xyz_dev_method",
        display_name="Friedland XYZ Development Method",
        test_data_dir=test_data_dir,
        ground_truth_path=ground_truth_path,
    )
    
    ground_truth = config.load_ground_truth()
    
    config.steps = [
        StepConfig(
            step_id="step_1",
            description="Load the triangle data and convert it to chainladder triangle",
            prompt_generator=steps.get_step_1_prompt,
            validator=lambda workspace_dir: validation.validate_step_1(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_2",
            description="Calculate volume-weighted average LDFs using latest 3 periods",
            prompt_generator=steps.get_step_2_prompt,
            validator=lambda workspace_dir: validation.validate_step_2(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_3",
            description="Calculate simple average LDFs using latest 5 periods",
            prompt_generator=steps.get_step_3_prompt,
            validator=lambda workspace_dir: validation.validate_step_3(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_4",
            description="Calculate CDFs with 1.00 tail factor from age 132",
            prompt_generator=steps.get_step_4_prompt,
            validator=lambda workspace_dir: validation.validate_step_4(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_5",
            description="Calculate ultimates using CDFs from step 4",
            prompt_generator=steps.get_step_5_prompt,
            validator=lambda workspace_dir: validation.validate_step_5(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_6",
            description="Calculate IBNR reserves",
            prompt_generator=steps.get_step_6_prompt,
            validator=lambda workspace_dir: validation.validate_step_6(workspace_dir, ground_truth)
        ),
    ]
    
    config.integration_prompt_generator = integration.generate_integration_prompt
    config.integration_validator = lambda workspace_dir: integration.validate_integration(workspace_dir, ground_truth)
    
    return config

