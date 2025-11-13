from pathlib import Path
from test_framework.method_config import MethodConfig, StepConfig
from methods.werner_modlin_b import steps, validation, integration


def get_config() -> MethodConfig:
    project_root = Path(__file__).parent.parent.parent
    test_data_dir = project_root / "test_data" / "werner_modlin_b"
    ground_truth_path = test_data_dir / "ground_truth.json"
    
    config = MethodConfig(
        method_name="werner_modlin_b",
        display_name="Werner-Modlin Loss Cost Ratemaking Method B",
        test_data_dir=test_data_dir,
        ground_truth_path=ground_truth_path,
    )
    
    ground_truth = config.load_ground_truth()
    
    config.steps = [
        StepConfig(
            step_id="step_1",
            description="Develop state losses to ultimate using countrywide LDFs",
            prompt_generator=steps.get_step_1_prompt,
            validator=lambda workspace_dir: validation.validate_step_1(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_2",
            description="Calculate loss trends from regional pure premium data",
            prompt_generator=steps.get_step_2_prompt,
            validator=lambda workspace_dir: validation.validate_step_2(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_3",
            description="Calculate total loss trend factors using Two-Step trending",
            prompt_generator=steps.get_step_3_prompt,
            validator=lambda workspace_dir: validation.validate_step_3(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_4",
            description="Calculate selected projected non-CAT pure premium",
            prompt_generator=steps.get_step_4_prompt,
            validator=lambda workspace_dir: validation.validate_step_4(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_5",
            description="Calculate credibility-weighted non-CAT pure premium",
            prompt_generator=steps.get_step_5_prompt,
            validator=lambda workspace_dir: validation.validate_step_5(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_6",
            description="Calculate variable permissible loss ratio (VPLR)",
            prompt_generator=steps.get_step_6_prompt,
            validator=lambda workspace_dir: validation.validate_step_6(workspace_dir, ground_truth)
        ),
        StepConfig(
            step_id="step_7",
            description="Calculate total indicated pure premium",
            prompt_generator=steps.get_step_7_prompt,
            validator=lambda workspace_dir: validation.validate_step_7(workspace_dir, ground_truth)
        ),
    ]
    
    config.integration_prompt_generator = integration.generate_integration_prompt
    config.integration_validator = lambda workspace_dir: integration.validate_integration(workspace_dir, ground_truth)
    
    return config

