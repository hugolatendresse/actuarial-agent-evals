from typing import Dict, Any


def get_step_1_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append(
        "[Frequency-Severity Method #1]: Develop CWP Count Triangle to Ultimate")
    prompt.append("")
    prompt.append(
        "Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Develop the closed with payment count triangle to ultimate")
    prompt.append(
        "using the latest 4 volume weighted average with a 1.00 tail factor.")
    prompt.append("")
    prompt.append("Store the result in a variable called: cwp_count_ultimate")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## SOLUTION COMPLETE - TESTED AND WORKING")

    return "\n".join(prompt)


def get_step_2_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append(
        "[Frequency-Severity Method #1]: Develop Reported Count Triangle to Ultimate")
    prompt.append("")
    prompt.append(
        "Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Develop the reported count triangle to ultimate")
    prompt.append(
        "using the latest 4 volume weighted average with a 1.00 tail factor.")
    prompt.append("")
    prompt.append(
        "Store the result in a variable called: reported_count_ultimate")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## SOLUTION COMPLETE - TESTED AND WORKING")

    return "\n".join(prompt)


def get_step_3_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append("[Frequency-Severity Method #1]: Calculate AY Ultimates")
    prompt.append("")
    prompt.append(
        "Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append(
        "Calculate the accident year ultimates by taking the average of the")
    prompt.append("CWP and reported count ultimates.")
    prompt.append("")
    prompt.append("Store the results in variables:")
    prompt.append(
        "- ay_ultimates: numpy array of ultimate counts by accident year")
    prompt.append("- total_frequency: sum of ay_ultimates")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## SOLUTION COMPLETE - TESTED AND WORKING")

    return "\n".join(prompt)


def get_step_4_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append(
        "[Frequency-Severity Method #1]: Project Ultimate Reported Severity")
    prompt.append("")
    prompt.append(
        "Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate severity as reported claims / reported count.")
    prompt.append(
        "Project ultimate severity using the latest 5 simple average with a 1.01 tail factor.")
    prompt.append(
        "Multiply ultimate severity by the frequency ultimates to get ultimate amounts by AY.")
    prompt.append("")
    prompt.append("Store the result in a variable called: ultimate_severity")
    prompt.append(
        "(This should be the total ultimate amount across all accident years)")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## SOLUTION COMPLETE - TESTED AND WORKING")

    return "\n".join(prompt)


def get_step_5_prompt(step_data: Dict[str, Any]) -> str:
    prompt = []
    prompt.append(
        "[Frequency-Severity Method #1]: Calculate Total Ultimate and IBNR")
    prompt.append("")
    prompt.append(
        "Examine the existing code to understand what has been set up.")
    prompt.append("")
    prompt.append("Calculate IBNR as ultimate minus latest reported claims.")
    prompt.append("")
    prompt.append("Store the results in variables:")
    prompt.append("- total_ultimate: total ultimate amount")
    prompt.append("- total_ibnr: total IBNR amount")
    prompt.append("")
    prompt.append("When complete and tested, add this exact line at the end:")
    prompt.append("## SOLUTION COMPLETE - TESTED AND WORKING")

    return "\n".join(prompt)
