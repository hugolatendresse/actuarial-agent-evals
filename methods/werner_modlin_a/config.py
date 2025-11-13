from pathlib import Path
from test_framework.method_config import MethodConfig, StepConfig
from methods.werner_modlin_a import steps, validation, integration


def get_config() -> MethodConfig:
    project_root = Path(__file__).parent.parent.parent
    test_data_dir = project_root / "test_data" / "werner_modlin_a"
    ground_truth_path = test_data_dir / "ground_truth.json"
    
    config = MethodConfig(
        method_name="werner_modlin_a",
        display_name="Werner-Modlin Loss Ratio Ratemaking Method",
        test_data_dir=test_data_dir,
        ground_truth_path=ground_truth_path,
    )
    
    ground_truth = config.load_ground_truth()
    
    config.steps = [
        StepConfig(
            step_id="step_1",
            description="Calculate CY earned premiums at current rate level",
            prompt_generator=steps.get_step_1_prompt,
            validator=lambda workspace_dir: validation.validate_step_1(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_2",
            description="Calculate 8-point exponential trend for average written premium",
            prompt_generator=steps.get_step_2_prompt,
            validator=lambda workspace_dir: validation.validate_step_2(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_3",
            description="Calculate total premium trend factors using Two-Step trending",
            prompt_generator=steps.get_step_3_prompt,
            validator=lambda workspace_dir: validation.validate_step_3(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_4",
            description="Calculate CY projected earned premiums at current rate level",
            prompt_generator=steps.get_step_4_prompt,
            validator=lambda workspace_dir: validation.validate_step_4(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_5",
            description="Develop losses to ultimate",
            prompt_generator=steps.get_step_5_prompt,
            validator=lambda workspace_dir: validation.validate_step_5(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_6",
            description="Calculate current loss trend (8-point)",
            prompt_generator=steps.get_step_6_prompt,
            validator=lambda workspace_dir: validation.validate_step_6(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_7",
            description="Calculate projected loss trend (4-point)",
            prompt_generator=steps.get_step_7_prompt,
            validator=lambda workspace_dir: validation.validate_step_7(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_8",
            description="Calculate total loss trend factors using Two-Step trending",
            prompt_generator=steps.get_step_8_prompt,
            validator=lambda workspace_dir: validation.validate_step_8(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_9",
            description="Calculate projected loss and LAE ratio",
            prompt_generator=steps.get_step_9_prompt,
            validator=lambda workspace_dir: validation.validate_step_9(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_10",
            description="Calculate variable permissible loss ratio",
            prompt_generator=steps.get_step_10_prompt,
            validator=lambda workspace_dir: validation.validate_step_10(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_11",
            description="Calculate indicated rate change",
            prompt_generator=steps.get_step_11_prompt,
            validator=lambda workspace_dir: validation.validate_step_11(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_12",
            description="Calculate classical credibility",
            prompt_generator=steps.get_step_12_prompt,
            validator=lambda workspace_dir: validation.validate_step_12(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_13",
            description="Calculate trended present rates indication",
            prompt_generator=steps.get_step_13_prompt,
            validator=lambda workspace_dir: validation.validate_step_13(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_14",
            description="Calculate credibility-weighted rate change",
            prompt_generator=steps.get_step_14_prompt,
            validator=lambda workspace_dir: validation.validate_step_14(workspace_dir, ground_truth)
        ),
    ]
    
    config.integration_prompt_generator = integration.generate_integration_prompt
    config.integration_validator = lambda workspace_dir: integration.validate_integration(workspace_dir, ground_truth)
    
    return config

