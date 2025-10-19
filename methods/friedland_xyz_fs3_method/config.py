from pathlib import Path
from test_framework.method_config import MethodConfig, StepConfig
from methods.friedland_xyz_fs3_method import steps, validation, integration


def get_config() -> MethodConfig:
    project_root = Path(__file__).parent.parent.parent
    test_data_dir = project_root / "test_data" / "friedland_xyz_fs3_method"
    ground_truth_path = test_data_dir / "ground_truth.json"
    
    config = MethodConfig(
        method_name="friedland_xyz_fs3_method",
        display_name="Friedland XYZ Frequency-Severity Method #3",
        test_data_dir=test_data_dir,
        ground_truth_path=ground_truth_path,
    )
    
    ground_truth = config.load_ground_truth()
    
    config.steps = [
        StepConfig(
            step_id="step_1",
            description="Develop reported count triangle and build disposal rate triangle",
            prompt_generator=steps.get_step_1_prompt,
            validator=lambda workspace_dir: validation.validate_step_1(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_2",
            description="Select disposal rates by age",
            prompt_generator=steps.get_step_2_prompt,
            validator=lambda workspace_dir: validation.validate_step_2(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_3",
            description="Calculate projected incremental closed with payment claim count",
            prompt_generator=steps.get_step_3_prompt,
            validator=lambda workspace_dir: validation.validate_step_3(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_4",
            description="Calculate incremental paid severity triangle",
            prompt_generator=steps.get_step_4_prompt,
            validator=lambda workspace_dir: validation.validate_step_4(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_5",
            description="Calculate adjusted to 2008 incremental paid severity",
            prompt_generator=steps.get_step_5_prompt,
            validator=lambda workspace_dir: validation.validate_step_5(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_6",
            description="Select adjusted incremental paid severities (ages 12-60)",
            prompt_generator=steps.get_step_6_prompt,
            validator=lambda workspace_dir: validation.validate_step_6(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_7",
            description="Calculate tail severities for ages 72+ and 84+",
            prompt_generator=steps.get_step_7_prompt,
            validator=lambda workspace_dir: validation.validate_step_7(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_8",
            description="Combine full array of selected severities",
            prompt_generator=steps.get_step_8_prompt,
            validator=lambda workspace_dir: validation.validate_step_8(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_9",
            description="Project unadjusted incremental paid amounts",
            prompt_generator=steps.get_step_9_prompt,
            validator=lambda workspace_dir: validation.validate_step_9(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_10",
            description="Calculate total ultimates by AY",
            prompt_generator=steps.get_step_10_prompt,
            validator=lambda workspace_dir: validation.validate_step_10(workspace_dir, ground_truth)
        ),
    ]
    
    config.integration_prompt_generator = integration.generate_integration_prompt
    config.integration_validator = lambda workspace_dir: integration.validate_integration(workspace_dir, ground_truth)
    
    return config

