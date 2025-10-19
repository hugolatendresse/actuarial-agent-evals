from typing import Dict, Any


def get_step_1_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 1."""
    prompt = []
    prompt.append("[Development Method - STEP 1]: Load Triangle Data")
    prompt.append("")
    prompt.append("Load the reported claims triangle from the CSV file and do any necessary data preparation for the chainladder method.")
    prompt.append("")
    prompt.append("Store the result in a variable called: triangle")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_2_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 2."""
    prompt = []
    prompt.append("[Development Method - STEP 2]: Calculate Volume-Weighted Average LDFs")
    prompt.append("")
    prompt.append("Calculate volume-weighted average Loss Development Factors using the latest 3 periods.")
    prompt.append("")
    prompt.append("Store the result in a variable called: ldfs_weighted")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_3_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 3."""
    prompt = []
    prompt.append("[Development Method - STEP 3]: Calculate Simple Average LDFs")
    prompt.append("")
    prompt.append("Calculate simple average Loss Development Factors using the latest 5 periods.")
    prompt.append("")
    prompt.append("Store the result in a variable called: ldfs_simple")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_4_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 4."""
    prompt = []
    prompt.append("[Development Method - STEP 4]: Apply Tail Factor and Calculate CDFs")
    prompt.append("")
    prompt.append("Apply a tail factor of 1.00 from age 132 to ultimate.")
    prompt.append("Calculate the CDFs using the volume-weighted LDFs.")
    prompt.append("")
    prompt.append("Store the results in variables:")
    prompt.append("- triangle_with_tail: triangle with tail factor applied")
    prompt.append("- ldfs_with_tail: LDFs including tail factor")
    prompt.append("- cdfs: CDFs")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_5_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 5."""
    prompt = []
    prompt.append("[Development Method - STEP 5]: Calculate Ultimate Claims")
    prompt.append("")
    prompt.append("Use the Chainladder method to calculate ultimate claims for each accident year.")
    prompt.append("Calculate the total ultimate across all years.")
    prompt.append("")
    prompt.append("Store the results in variables:")
    prompt.append("- cl_result: the fitted Chainladder model result")
    prompt.append("- ultimates: ultimate values by accident year")
    prompt.append("- total_ultimate: sum of all ultimates")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_6_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 6."""
    prompt = []
    prompt.append("[Development Method - STEP 6]: Calculate IBNR Reserves")
    prompt.append("")
    prompt.append("Extract IBNR reserves for each accident year and calculate the total.")
    prompt.append("")
    prompt.append("Store the results in variables:")
    prompt.append("- ibnr: IBNR values by accident year")
    prompt.append("- total_ibnr: sum of all IBNR")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)

