from typing import Dict, Any


def get_step_1_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #2]: Develop Reported Count to Ultimate")
    prompt.append("")
    prompt.append("Load the reported claim count triangle and develop it to ultimate")
    prompt.append("using the latest 4 volume weighted average with a 1.00 tail factor.")
    prompt.append("")
    prompt.append("Store the results in variables:")
    prompt.append("- count_ultimate: the ultimate triangle")
    prompt.append("- count_total_ultimate: sum of all ultimate counts")
    prompt.append("- count_ultimates_by_ay: array of ultimate counts by accident year")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_2_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #2]: Trend Claim Counts (AY 2002-2006)")
    prompt.append("")
    prompt.append("Trend the counts for accident years 2002-2006")
    prompt.append("to 2008 using a claim count trend of -1.5%.")
    prompt.append("")
    prompt.append("Formula: trended_count = ultimate_count * (1 + trend)^(2008 - AY)")
    prompt.append("")
    prompt.append("Store the result in a dictionary called: trended_count_dict")
    prompt.append("with keys as accident years (2002-2006) and values as trended counts")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_3_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #2]: Calculate On-Level Earned Premiums")
    prompt.append("")
    prompt.append("Load the earned premium and rate changes data.")
    prompt.append("Calculate on-level factors by computing cumulative rate factors and")
    prompt.append("then calculating the ratio to bring all premiums to 2008 rate level.")
    prompt.append("")
    prompt.append("Store the result in a list called: onlevel_premiums")
    prompt.append("(ordered by accident year 1998-2008)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_4_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #2]: Calculate Trended Frequency to OLEP (AY 2002-2006)")
    prompt.append("")
    prompt.append("Using the trended counts and the on-level premiums,")
    prompt.append("calculate the frequency (to premium, in 000s).")
    prompt.append("")
    prompt.append("Calculate this for accident years 2002-2006.")
    prompt.append("")
    prompt.append("Store the result in a dictionary called: trended_freq_to_olep")
    prompt.append("with keys as accident years (2002-2006) and values as frequencies")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_5_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #2]: Select 2008 Frequency Level")
    prompt.append("")
    prompt.append("Select the 2008 frequency level as the average of the frequencies")
    prompt.append("for accident years 2005 and 2006.")
    prompt.append("")
    prompt.append("Store the result in a variable called: selected_2008_freq")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_6_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #2]: Calculate Unadjusted Frequencies (All AYs)")
    prompt.append("")
    prompt.append("Using the selected 2008 frequency, calculate unadjusted frequencies")
    prompt.append("for all accident years (1998-2008).")
    prompt.append("")
    prompt.append("Store the result in a list called: unadjusted_freqs")
    prompt.append("(ordered by accident year 1998-2008)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_7_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #2]: Project Ultimate Claim Counts (All AYs)")
    prompt.append("")
    prompt.append("Using the unadjusted frequencies and the earned premiums,")
    prompt.append("project ultimate claim counts for all accident years (1998-2008):")
    prompt.append("")
    prompt.append("Store the result in a list called: projected_counts")
    prompt.append("(ordered by accident year 1998-2008)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_8_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #2]: Develop Severity to Ultimate")
    prompt.append("")
    prompt.append("Load the reported claims triangle and the reported count triangle.")
    prompt.append("Calculate severity.")
    prompt.append("Develop severity to ultimate using the latest 5 simple average with a 1.01 tail factor.")
    prompt.append("")
    prompt.append("Store the results in variables:")
    prompt.append("- severity_ultimate: the ultimate severity triangle")
    prompt.append("- severity_ultimates_by_ay: array of ultimate severities by accident year")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_9_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #2]: Adjust Severities to 2008 Level (AY 1998-2006)")
    prompt.append("")
    prompt.append("Adjust severities for accident years 1998-2006 to 2008 level using:")
    prompt.append("- Severity trend: 5% per year")
    prompt.append("- Tort reform changes effective 1/1/2006 have reduced expected losses by 10.7% in")
    prompt.append("  accident year 2006, and by 33% in accident years 2007 and later, compared to")
    prompt.append("  2005 and earlier years.")
    prompt.append("")
    prompt.append("Store the result in a list called: adjusted_severities")
    prompt.append("(ordered by accident year 1998-2006, 9 values total)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_10_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #2]: Select 2008 Severity Level")
    prompt.append("")
    prompt.append("From the adjusted severities, make a selection for the 2008 severity using the latest 5 excluding high/low.")
    prompt.append("")
    prompt.append("Store the result in a variable called: selected_2008_severity")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_11_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #2]: Calculate Unadjusted Severities (AY 2007-2008)")
    prompt.append("")
    prompt.append("De-trend the selected 2008 severity to get the")
    prompt.append("unadjusted severities for AY 2007-2008 using the 5% severity trend.")
    prompt.append("")
    prompt.append("Store the result in a list called: unadjusted_severities_latest2")
    prompt.append("(ordered as [2007, 2008])")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)


def get_step_12_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #2]: Calculate Ultimate and IBNR (AY 2007-2008)")
    prompt.append("")
    prompt.append("Using the projected counts and the unadjusted severities, calculate the ultimate and IBNR for AY 2007-2008.")
    prompt.append("Store the results in variables:")
    prompt.append("- total_ultimate_latest2: total ultimate for AY 2007-2008")
    prompt.append("- total_ibnr_latest2: total IBNR for AY 2007-2008")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## STEP COMPLETE - TESTED AND WORKING")
    
    return "\n".join(prompt)

