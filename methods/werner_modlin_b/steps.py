from typing import Dict, Any


def get_step_1_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append(
        "[Werner-Modlin Method B]: Develop State Losses to Ultimate using Countrywide LDFs")
    prompt.append("")
    prompt.append(
        "Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append(
        "Use the countrywide triangle to calculate LDFs using chainladder method with")
    prompt.append(
        "all years simple average, 1% tail factor at age 63, then apply the resulting CDFs to")
    prompt.append("the state reported losses to develop them to ultimate.")
    prompt.append("")
    prompt.append(
        "Store the result in a variable called: state_ultimate_losses")
    prompt.append("(as a numpy array)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## SOLUTION COMPLETE - TESTED AND WORKING")

    return "\n".join(prompt)


def get_step_2_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append(
        "[Werner-Modlin Method B]: Calculate Loss Trends from Regional Pure Premium Data")
    prompt.append("")
    prompt.append(
        "Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Using the regional quarterly pure premium data, calculate:")
    prompt.append("- Current loss trend using 8-point exponential trend fit")
    prompt.append("- Projected loss trend using 4-point exponential trend fit")
    prompt.append("")
    prompt.append("Store the results in variables called:")
    prompt.append("- current_loss_trend_annual: annual trend rate as decimal")
    prompt.append(
        "- projected_loss_trend_annual: annual trend rate as decimal")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## SOLUTION COMPLETE - TESTED AND WORKING")

    return "\n".join(prompt)


def get_step_3_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append(
        "[Werner-Modlin Method B]: Calculate Total Loss Trend Factors (Two-Step)")
    prompt.append("")
    prompt.append(
        "Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append(
        "Calculate total loss trend factors for each accident year (2011-2015) using")
    prompt.append(
        "the Two-Step trending approach. Policy term is 12 months, rates will be in")
    prompt.append("effect for 12 months starting 1/1/2017.")
    prompt.append("")
    prompt.append(
        "Store the result in a variable called: total_loss_trend_factors")
    prompt.append("(as a numpy array of 5 values)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## SOLUTION COMPLETE - TESTED AND WORKING")

    return "\n".join(prompt)


def get_step_4_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append(
        "[Werner-Modlin Method B]: Calculate Selected Projected Non-CAT Pure Premium")
    prompt.append("")
    prompt.append(
        "Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append(
        "Apply trend factors to ultimate losses, adjust for ULAE, and calculate the")
    prompt.append(
        "selected projected non-CAT pure premium per exposure using an all-years weighted average.")
    prompt.append("")
    prompt.append("Use ULAE factor: 1.011812")
    prompt.append("")
    prompt.append(
        "Store the result in a variable called: selected_projected_non_cat_pure_premium")
    prompt.append("(as decimal)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## SOLUTION COMPLETE - TESTED AND WORKING")

    return "\n".join(prompt)


def get_step_5_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append(
        "[Werner-Modlin Method B]: Calculate Credibility-Weighted Non-CAT Pure Premium")
    prompt.append("")
    prompt.append(
        "Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append(
        "Using classical credibility and the provided info, weight the selected projected")
    prompt.append(
        "non-CAT pure premium with the regional non-CAT pure premium.")
    prompt.append("")
    prompt.append("Given:")
    prompt.append("- Total reported claims (5-year): 683")
    prompt.append("- Claims for full credibility: 1082")
    prompt.append("- Regional non-CAT pure premium: $585.75")
    prompt.append("")
    prompt.append(
        "Store the result in a variable called: credibility_weighted_non_cat_pure_premium")
    prompt.append("(as decimal)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## SOLUTION COMPLETE - TESTED AND WORKING")

    return "\n".join(prompt)


def get_step_6_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append(
        "[Werner-Modlin Method B]: Calculate Variable Permissible Loss Ratio (VPLR)")
    prompt.append("")
    prompt.append(
        "Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate the variable permissible loss ratio given:")
    prompt.append("- Variable expense provision: 13.8%")
    prompt.append("- Profit and contingency provision: 5%")
    prompt.append("")
    prompt.append("Store the result in a variable called: vplr")
    prompt.append("(as decimal)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## SOLUTION COMPLETE - TESTED AND WORKING")

    return "\n".join(prompt)


def get_step_7_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append(
        "[Werner-Modlin Method B]: Calculate Total Indicated Pure Premium")
    prompt.append("")
    prompt.append(
        "Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate the total indicated pure premium.")
    prompt.append("")
    prompt.append("Given:")
    prompt.append("- Total CAT pure premium: $103.85")
    prompt.append("- Projected net reinsurance cost per exposure: $15.68")
    prompt.append("- Projected fixed expense per exposure: $77.74")
    prompt.append("")
    prompt.append(
        "Store the result in a variable called: total_indicated_pure_premium")
    prompt.append("(as decimal)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## SOLUTION COMPLETE - TESTED AND WORKING")

    return "\n".join(prompt)
