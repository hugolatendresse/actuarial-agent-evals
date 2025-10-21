from typing import Dict, Any


def get_step_1_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #3]: Build Disposal Rate Triangle")
    prompt.append("")
    prompt.append("Build a disposal rate triangle using the closed with payment claim count triangle")
    prompt.append("and the reported count ultimates.")
    prompt.append("")
    prompt.append("Store the result in a variable called: disposal_rate_tri")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_2_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #3]: Select Disposal Rates by Age")
    prompt.append("")
    prompt.append("For each development age column in the disposal rate triangle,")
    prompt.append("calculate the simple average of the latest 2 values.")
    prompt.append("Then append 1.00 as the tail value at age 108 (ultimate disposal rate).")
    prompt.append("")
    prompt.append("Store the result in a variable called: selected_disposal_rates (list or array with 9 values)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_3_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #3]: Calculate Projected Incremental Closed Claim Count")
    prompt.append("")
    prompt.append("Calculate the projected incremental closed with payment claim count triangle.")
    prompt.append("")
    prompt.append("Store the result in a variable called: projected_incremental_cwp (2D array)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_4_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #3]: Calculate Incremental Paid Severity Triangle")
    prompt.append("")
    prompt.append("Calculate the incremental paid severity triangle.")
    prompt.append("")
    prompt.append("Store the result in a variable called: incremental_severity_tri")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_5_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #3]: Adjust Incremental Paid Severity to 2008")
    prompt.append("")
    prompt.append("Adjust the incremental paid severity triangle to 2008 levels:")
    prompt.append("- Apply 5% annual severity trend")
    prompt.append("- Tort reform changes effective 1/1/2006 have reduced expected losses by 10.7% in accident year 2006, and by 33% in accident years 2007 and later, compared to 2005 and earlier years.")
    prompt.append("")
    prompt.append("Store the result in a variable called: adjusted_severity (2D numpy array)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_6_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #3]: Select Adjusted Severities for Ages 12-60")
    prompt.append("")
    prompt.append("Select adjusted incremental paid severities for ages 12-60 using latest 2 simple average.")
    prompt.append("")
    prompt.append("Store the result in a variable called: selected_adjusted_severities (list or array with 5 values)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_7_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #3]: Calculate Tail Severities")
    prompt.append("")
    prompt.append("Calculate tail severity for ages 72+ and 84+.")
    prompt.append("")
    prompt.append("Store the results in variables:")
    prompt.append("- tail_severity_72: tail severity for age 72+")
    prompt.append("- tail_severity_84: tail severity for age 84+")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_8_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #3]: Combine Full Array of Selected Severities")
    prompt.append("")
    prompt.append("Combine selected severities from ages 12 to 108-Ultimate into a single array.")
    prompt.append("")
    prompt.append("Store the result in a variable called: full_selected_severities (list or array with 9 values)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_9_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #3]: Project Unadjusted Incremental Paid Amounts")
    prompt.append("")
    prompt.append("Project unadjusted incremental paid amounts.")
    prompt.append("")
    prompt.append("Store the result in a variable called: projected_incremental_paid (2D array in thousands)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_10_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #3]: Calculate Total Ultimates by AY")
    prompt.append("")
    prompt.append("Calculate total ultimates by accident year.")
    prompt.append("")
    prompt.append("Store the result in a variable called: total_ultimates_by_ay (array in thousands)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)

