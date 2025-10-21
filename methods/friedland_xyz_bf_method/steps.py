from typing import Dict, Any


def get_step_1_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 1: Calculate BF Ultimates."""
    prompt = []
    prompt.append("[Bornhuetter-Ferguson Method]: Calculate Ultimate Claims")
    prompt.append("")
    prompt.append("Using the provided triangle with development patterns, earned premium data, and expected claim ratios,")
    prompt.append("calculate ultimate claims using the Bornhuetter-Ferguson method.")
    prompt.append("")
    prompt.append("Store the result in a variable called: total_bf_ultimate")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_2_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 2: Extract BF IBNR."""
    prompt = []
    prompt.append("[Bornhuetter-Ferguson Method]: Calculate IBNR")
    prompt.append("")
    prompt.append("Calculate the IBNR reserves from the Bornhuetter-Ferguson model.")
    prompt.append("")
    prompt.append("Store the result in a variable called: total_bf_ibnr")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)

