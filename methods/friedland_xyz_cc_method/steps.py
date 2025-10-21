from typing import Dict, Any


def get_step_1_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 1."""
    prompt = []
    prompt.append("[Cape Cod Method]: Calculate Current Level Earned Premium")
    prompt.append("")
    prompt.append("Using the earned premium and rate changes data, calculate the current level earned premium.")
    prompt.append("")
    prompt.append("Store the result in a variable called: current_level_earned_premium (as a pandas Series or array)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_2_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 2."""
    prompt = []
    prompt.append("[Cape Cod Method]: Calculate Tort Reform On-Level Factors")
    prompt.append("")
    prompt.append("Tort reform effective 1/1/2006 reduced expected losses by 10.7% in AY 2006,")
    prompt.append("and by 33% in AY 2007 and later, compared to AY 2005 and earlier.")
    prompt.append("Calculate the factors to adjust all years to AY 2008 tort law level.")
    prompt.append("")
    prompt.append("Store the result in a variable called: tort_reform_factors (as a pandas Series or array)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_3_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 3."""
    prompt = []
    prompt.append("[Cape Cod Method]: Calculate Adjusted Reported Claims")
    prompt.append("")
    prompt.append("Adjust the latest reported claims for tort reform to bring all years to AY 2008 tort law level.")
    prompt.append("")
    prompt.append("Store the result in a variable called: adjusted_reported_claims (as a pandas Series or array)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_4_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 4."""
    prompt = []
    prompt.append("[Cape Cod Method]: Calculate Cape Cod Ultimate Claims")
    prompt.append("")
    prompt.append("Using the tort-reform-adjusted triangle, on-level premium, latest-2 volume weighted LDFs,")
    prompt.append("1.05 tail factor, and 3.425% premium trend, calculate Cape Cod ultimate claims.")
    prompt.append("Adjust the results back to original tort law level.")
    prompt.append("")
    prompt.append("Store the result in a variable called: total_cc_ultimate")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_5_prompt(step_data: Dict[str, Any]) -> str:
    """Generate prompt for step 5."""
    prompt = []
    prompt.append("[Cape Cod Method]: Calculate Cape Cod IBNR")
    prompt.append("")
    prompt.append("Calculate IBNR and adjust back to original tort law level.")
    prompt.append("")
    prompt.append("Store the result in a variable called: total_cc_ibnr")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)

