from typing import Dict, Any


def get_step_1_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate CY Earned Premiums at Current Rate Level")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate calendar year earned premiums adjusted to the current rate level.")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_1_earned_premium_crl")
    prompt.append("(as a numpy array of 5 values for calendar years 2011-2015)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_2_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate 8-Point Exponential Trend for Average Written Premium")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Using the quarterly written premium and exposure data, calculate the")
    prompt.append("8-point exponential trend for average written premiums at current rate level.")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_2_premium_trend")
    prompt.append("(annual trend rate as decimal)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_3_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate Total Premium Trend Factors (Two-Step Trending)")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate total premium trend factors for each calendar year using the Two-Step")
    prompt.append("trending approach. Policy term is 6 months, rates will be in effect for 12 months")
    prompt.append("starting 1/1/2017.")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_3_total_trend_factors")
    prompt.append("(as a numpy array of 5 values for calendar years 2011-2015)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_4_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate CY Projected Earned Premiums at Current Rate Level")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate projected earned premiums at current rate level for each calendar year.")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_4_projected_earned_premium")
    prompt.append("(as a numpy array of 5 values for calendar years 2011-2015)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_5_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Develop Losses to Ultimate")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Develop the reported loss+ALAE triangle to ultimate using all-years average")
    prompt.append("excluding high and low, with a 1.0 tail factor at age 63.")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_5_ultimate_losses")
    prompt.append("(as a numpy array containing ultimate losses for all accident years)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_6_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate Current Loss Trend (8-point)")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Using the regional loss trend data, calculate the current loss trend")
    prompt.append("by fitting 8-point exponential trends to frequency and severity separately,")
    prompt.append("then combining them.")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_6_current_loss_trend")
    prompt.append("(annual combined loss trend as decimal)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_7_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate Projected Loss Trend (4-point)")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Using the regional loss trend data, calculate the projected loss trend")
    prompt.append("by fitting 4-point exponential trends to frequency and severity separately,")
    prompt.append("then combining them.")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_7_projected_loss_trend")
    prompt.append("(annual combined loss trend as decimal)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_8_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate Total Loss Trend Factors (Two-Step)")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate total loss trend factors for each accident year (2011-2015) using")
    prompt.append("the Two-Step trending approach. Policy term is 6 months, rates will be in")
    prompt.append("effect for 12 months starting 1/1/2017.")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_8_total_loss_trend_factors")
    prompt.append("(as a numpy array of 5 values for accident years 2011-2015)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_9_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate Projected Loss and LAE Ratio")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate the projected loss and LAE ratio as a weighted average,")
    prompt.append("applying the ULAE factor of 1.143.")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_9_projected_loss_lae_ratio")
    prompt.append("(as decimal")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_10_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate Variable Permissible Loss Ratio")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate the variable permissible loss ratio given:")
    prompt.append("- Variable expense provision: 16.9956%")
    prompt.append("- Underwriting profit provision: 5%")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_10_vplr")
    prompt.append("(as decimal)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_11_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate Indicated Rate Change")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate the indicated rate change using the loss ratio method.")
    prompt.append("Fixed expense provision is 11.2867%.")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_11_indicated_rate_change")
    prompt.append("(as decimal)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_12_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate Classical Credibility")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate classical credibility given:")
    prompt.append("- Total claims in historical period: 700")
    prompt.append("- Claims for full credibility: 1082")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_12_credibility")
    prompt.append("(as decimal)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_13_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate Trended Present Rates Indication")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate the trended present rates indication for the complement of credibility.")
    prompt.append("The last rate change was effective 1/1/2016, and given:")
    prompt.append("- Latest indicated rate change: 13.2%")
    prompt.append("- Last rate change taken: 5%")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_13_trended_present_rates")
    prompt.append("(as decimal)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_14_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Werner-Modlin Method]: Calculate Credibility-Weighted Rate Change")
    prompt.append("")
    prompt.append("Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate the final credibility-weighted rate change, combining the")
    prompt.append("indicated rate change with the trended present rates indication.")
    prompt.append("")
    prompt.append("Store the result in a variable called: step_14_credibility_weighted_rate_change")
    prompt.append("(as decimal)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)

