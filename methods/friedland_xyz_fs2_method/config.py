from pathlib import Path
from test_framework.method_config import MethodConfig, StepConfig
from methods.friedland_xyz_fs2_method import steps, validation, integration


def get_config() -> MethodConfig:
    project_root = Path(__file__).parent.parent.parent
    test_data_dir = project_root / "test_data" / "friedland_xyz_fs2_method"
    ground_truth_path = test_data_dir / "ground_truth.json"
    
    config = MethodConfig(
        method_name="friedland_xyz_fs2_method",
        display_name="Friedland XYZ Frequency-Severity Method #2",
        test_data_dir=test_data_dir,
        ground_truth_path=ground_truth_path,
    )
    
    ground_truth = config.load_ground_truth()
    
    config.steps = [
        StepConfig(
            step_id="step_1",
            description="Develop reported count to ultimate",
            prompt_generator=steps.get_step_1_prompt,
            validator=lambda workspace_dir: validation.validate_step_1(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_2",
            description="Trend claim counts to 2008 (AY 2002-2006)",
            prompt_generator=steps.get_step_2_prompt,
            validator=lambda workspace_dir: validation.validate_step_2(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_3",
            description="Calculate on-level earned premiums",
            prompt_generator=steps.get_step_3_prompt,
            validator=lambda workspace_dir: validation.validate_step_3(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_4",
            description="Calculate trended frequency to OLEP (AY 2002-2006)",
            prompt_generator=steps.get_step_4_prompt,
            validator=lambda workspace_dir: validation.validate_step_4(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_5",
            description="Select 2008 frequency level",
            prompt_generator=steps.get_step_5_prompt,
            validator=lambda workspace_dir: validation.validate_step_5(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_6",
            description="Calculate unadjusted frequencies for all AYs",
            prompt_generator=steps.get_step_6_prompt,
            validator=lambda workspace_dir: validation.validate_step_6(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_7",
            description="Project ultimate claim counts",
            prompt_generator=steps.get_step_7_prompt,
            validator=lambda workspace_dir: validation.validate_step_7(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_8",
            description="Develop severity to ultimate",
            prompt_generator=steps.get_step_8_prompt,
            validator=lambda workspace_dir: validation.validate_step_8(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_9",
            description="Adjust severities to 2008 level (AY 1998-2006)",
            prompt_generator=steps.get_step_9_prompt,
            validator=lambda workspace_dir: validation.validate_step_9(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_10",
            description="Select 2008 severity",
            prompt_generator=steps.get_step_10_prompt,
            validator=lambda workspace_dir: validation.validate_step_10(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_11",
            description="Get unadjusted severities for AY 2007-2008",
            prompt_generator=steps.get_step_11_prompt,
            validator=lambda workspace_dir: validation.validate_step_11(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_12",
            description="Calculate ultimate and IBNR for latest 2 AYs",
            prompt_generator=steps.get_step_12_prompt,
            validator=lambda workspace_dir: validation.validate_step_12(workspace_dir, ground_truth)
        ),
    ]
    
    config.integration_prompt_generator = integration.generate_integration_prompt
    config.integration_validator = lambda workspace_dir: integration.validate_integration(workspace_dir, ground_truth)
    
    return config

