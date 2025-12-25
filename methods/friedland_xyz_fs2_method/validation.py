import subprocess
import numpy as np
from pathlib import Path
from typing import Dict, Any


SOLUTION_FILENAME = "step_solution.py"


def validate_step_1(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

import numpy as np
assert 'count_total_ultimate' in dir(), "Variable 'count_total_ultimate' not found"
assert 'count_ultimates_by_ay' in dir(), "Variable 'count_ultimates_by_ay' not found"

if hasattr(count_total_ultimate, 'sum'):
    count_total = float(count_total_ultimate.sum().sum())
else:
    count_total = float(count_total_ultimate)

print(f"COUNT_TOTAL_ULTIMATE: {count_total:.2f}")

if hasattr(count_ultimates_by_ay, 'values'):
    count_by_ay = count_ultimates_by_ay.values[0, 0, :, -1]
else:
    count_by_ay = count_ultimates_by_ay

for i, val in enumerate(count_by_ay):
    print(f"AY_{i}: {val:.2f}")
"""

    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)

    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}

    output = result.stdout
    gt_total = ground_truth["step_1"]["count_total_ultimate"]
    gt_by_ay = ground_truth["step_1"]["count_ultimates_by_ay"]

    try:
        count_total = None
        count_by_ay = []

        for line in output.split('\n'):
            if 'COUNT_TOTAL_ULTIMATE:' in line:
                count_total = float(line.split(':')[1].strip())
            elif line.startswith('AY_'):
                count_by_ay.append(float(line.split(':')[1].strip()))

        if count_total is None:
            return {"passed": False, "error": "Could not parse count_total_ultimate from output"}

        total_match = np.isclose(count_total, gt_total, rtol=0.01)
        ay_match = len(count_by_ay) == len(gt_by_ay) and all(
            np.isclose(a, b, rtol=0.01) for a, b in zip(count_by_ay, gt_by_ay)
        )

        passed = total_match and ay_match

        errors = []
        if not total_match:
            errors.append(
                f"Total count ultimate: expected {gt_total:,.2f}, got {count_total:,.2f}")
        if not ay_match:
            errors.append(f"Count by AY mismatch")

        return {
            "passed": passed,
            "error": None if passed else "; ".join(errors),
            "count_total_ultimate": count_total
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_2(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

assert 'trended_count_dict' in dir(), "Variable 'trended_count_dict' not found"

for year in [2002, 2003, 2004, 2005, 2006]:
    count = trended_count_dict[year]
    print(f"AY_{year}: {count:.0f}")
"""

    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)

    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}

    output = result.stdout
    gt_trended = ground_truth["step_2"]["trended_counts"]

    try:
        trended_counts = {}
        for line in output.split('\n'):
            if line.startswith('AY_'):
                year = int(line.split('_')[1].split(':')[0])
                count = float(line.split(':')[1].strip())
                trended_counts[year] = count

        passed = all(
            np.isclose(trended_counts.get(int(year), 0),
                       gt_trended[year], rtol=0.01)
            for year in gt_trended.keys()
        )

        return {
            "passed": passed,
            "error": None if passed else "Trended counts mismatch",
            "trended_counts": trended_counts
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_3(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

assert 'onlevel_premiums' in dir(), "Variable 'onlevel_premiums' not found"

for i, olep in enumerate(onlevel_premiums):
    print(f"OLEP_{i}: {olep:.2f}")
"""

    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)

    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}

    output = result.stdout
    gt_olep = ground_truth["step_3"]["onlevel_premiums"]

    try:
        onlevel_premiums = []
        for line in output.split('\n'):
            if line.startswith('OLEP_'):
                olep = float(line.split(':')[1].strip())
                onlevel_premiums.append(olep)

        passed = len(onlevel_premiums) == len(gt_olep) and all(
            np.isclose(a, b, rtol=0.01) for a, b in zip(onlevel_premiums, gt_olep)
        )

        return {
            "passed": passed,
            "error": None if passed else "On-level premiums mismatch",
            "onlevel_premiums": onlevel_premiums
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_4(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

assert 'trended_freq_to_olep' in dir(), "Variable 'trended_freq_to_olep' not found"

for year in [2002, 2003, 2004, 2005, 2006]:
    freq = trended_freq_to_olep[year]
    print(f"FREQ_{year}: {freq:.4f}")
"""

    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)

    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}

    output = result.stdout
    gt_freq = ground_truth["step_4"]["trended_freq_to_olep"]

    try:
        trended_freq = {}
        for line in output.split('\n'):
            if line.startswith('FREQ_'):
                year = int(line.split('_')[1].split(':')[0])
                freq = float(line.split(':')[1].strip())
                trended_freq[year] = freq

        passed = all(
            np.isclose(trended_freq.get(int(year), 0),
                       gt_freq[year], atol=0.0001)
            for year in gt_freq.keys()
        )

        return {
            "passed": passed,
            "error": None if passed else "Trended frequency to OLEP mismatch",
            "trended_freq_to_olep": trended_freq
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_5(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

assert 'selected_2008_freq' in dir(), "Variable 'selected_2008_freq' not found"

print(f"SELECTED_2008_FREQ: {selected_2008_freq:.4f}")
"""

    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)

    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}

    output = result.stdout
    gt_freq = ground_truth["step_5"]["selected_2008_freq"]

    if "SELECTED_2008_FREQ:" in output:
        freq_str = output.split("SELECTED_2008_FREQ:")[1].strip().split()[0]
        actual_freq = float(freq_str)

        passed = np.isclose(actual_freq, gt_freq, atol=0.0001)

        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_freq:.4f}, got {actual_freq:.4f}",
            "selected_2008_freq": actual_freq
        }

    return {"passed": False, "error": "Could not parse selected_2008_freq from output"}


def validate_step_6(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

assert 'unadjusted_freqs' in dir(), "Variable 'unadjusted_freqs' not found"

for i, freq in enumerate(unadjusted_freqs):
    print(f"FREQ_{i}: {freq:.4f}")
"""

    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)

    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}

    output = result.stdout
    gt_freqs = ground_truth["step_6"]["unadjusted_freqs"]

    try:
        unadjusted_freqs = []
        for line in output.split('\n'):
            if line.startswith('FREQ_'):
                freq = float(line.split(':')[1].strip())
                unadjusted_freqs.append(freq)

        passed = len(unadjusted_freqs) == len(gt_freqs) and all(
            np.isclose(a, b, atol=0.0001) for a, b in zip(unadjusted_freqs, gt_freqs)
        )

        return {
            "passed": passed,
            "error": None if passed else "Unadjusted frequencies mismatch",
            "unadjusted_freqs": unadjusted_freqs
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_7(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

assert 'projected_counts' in dir(), "Variable 'projected_counts' not found"

for i, count in enumerate(projected_counts):
    print(f"COUNT_{i}: {count:.0f}")
"""

    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)

    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}

    output = result.stdout
    gt_counts = ground_truth["step_7"]["projected_counts"]

    try:
        projected_counts = []
        for line in output.split('\n'):
            if line.startswith('COUNT_'):
                count = float(line.split(':')[1].strip())
                projected_counts.append(count)

        passed = len(projected_counts) == len(gt_counts) and all(
            abs(a - b) < 5 for a, b in zip(projected_counts, gt_counts)
        )

        return {
            "passed": passed,
            "error": None if passed else "Projected counts mismatch",
            "projected_counts": projected_counts
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_8(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

assert 'severity_ultimates_by_ay' in dir(), "Variable 'severity_ultimates_by_ay' not found"

if hasattr(severity_ultimates_by_ay, 'values'):
    sev_by_ay = severity_ultimates_by_ay.values[0, 0, :, -1]
else:
    sev_by_ay = severity_ultimates_by_ay

for i, val in enumerate(sev_by_ay):
    print(f"SEV_{i}: {val:.2f}")
"""

    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)

    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}

    return {
        "passed": True,
        "error": None
    }


def validate_step_9(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

assert 'adjusted_severities' in dir(), "Variable 'adjusted_severities' not found"

for i, sev in enumerate(adjusted_severities):
    print(f"SEV_{i}: {sev:.0f}")
"""

    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)

    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}

    output = result.stdout
    gt_sevs = ground_truth["step_9"]["adjusted_severities"]

    try:
        adjusted_severities = []
        for line in output.split('\n'):
            if line.startswith('SEV_'):
                sev = float(line.split(':')[1].strip())
                adjusted_severities.append(sev)

        passed = len(adjusted_severities) == len(gt_sevs) and all(
            abs(a - b) < 10 for a, b in zip(adjusted_severities, gt_sevs)
        )

        return {
            "passed": passed,
            "error": None if passed else "Adjusted severities mismatch",
            "adjusted_severities": adjusted_severities
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_10(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

assert 'selected_2008_severity' in dir(), "Variable 'selected_2008_severity' not found"

print(f"SELECTED_2008_SEVERITY: {selected_2008_severity:.0f}")
"""

    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)

    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}

    output = result.stdout
    gt_sev = ground_truth["step_10"]["selected_2008_severity"]

    if "SELECTED_2008_SEVERITY:" in output:
        sev_str = output.split("SELECTED_2008_SEVERITY:")[1].strip().split()[0]
        actual_sev = float(sev_str)

        passed = abs(actual_sev - gt_sev) < 10

        return {
            "passed": passed,
            "error": None if passed else f"Expected {gt_sev:,.0f}, got {actual_sev:,.0f}",
            "selected_2008_severity": actual_sev
        }

    return {"passed": False, "error": "Could not parse selected_2008_severity from output"}


def validate_step_11(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

assert 'unadjusted_severities_latest2' in dir(), "Variable 'unadjusted_severities_latest2' not found"

for i, sev in enumerate(unadjusted_severities_latest2):
    print(f"SEV_{i}: {sev:.0f}")
"""

    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)

    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}

    output = result.stdout
    gt_sevs = ground_truth["step_11"]["unadjusted_severities_latest2"]

    try:
        unadj_sevs = []
        for line in output.split('\n'):
            if line.startswith('SEV_'):
                sev = float(line.split(':')[1].strip())
                unadj_sevs.append(sev)

        passed = len(unadj_sevs) == len(gt_sevs) and all(
            abs(a - b) < 10 for a, b in zip(unadj_sevs, gt_sevs)
        )

        return {
            "passed": passed,
            "error": None if passed else "Unadjusted severities for latest 2 AYs mismatch",
            "unadjusted_severities_latest2": unadj_sevs
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}


def validate_step_12(workspace_dir: Path, ground_truth: Dict[str, Any]) -> Dict[str, Any]:
    check_code = """
import sys
sys.path.insert(0, '.')
exec(open('step_solution.py').read().replace('## SOLUTION COMPLETE - TESTED AND WORKING', ''))

assert 'total_ultimate_latest2' in dir(), "Variable 'total_ultimate_latest2' not found"
assert 'total_ibnr_latest2' in dir(), "Variable 'total_ibnr_latest2' not found"

if hasattr(total_ultimate_latest2, 'sum'):
    ult_val = float(total_ultimate_latest2.sum().sum())
else:
    ult_val = float(total_ultimate_latest2)

if hasattr(total_ibnr_latest2, 'sum'):
    ibnr_val = float(total_ibnr_latest2.sum().sum())
else:
    ibnr_val = float(total_ibnr_latest2)

print(f"TOTAL_ULTIMATE_LATEST2: {ult_val:.2f}")
print(f"TOTAL_IBNR_LATEST2: {ibnr_val:.2f}")
"""

    with open(workspace_dir / "validate.py", 'w') as f:
        f.write(check_code)

    result = subprocess.run(
        ["python", "validate.py"],
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        return {"passed": False, "error": f"Execution error: {result.stderr}"}

    output = result.stdout
    gt_ultimate = ground_truth["step_12"]["total_ultimate_latest2"]
    gt_ibnr = ground_truth["step_12"]["total_ibnr_latest2"]

    try:
        total_ultimate = None
        total_ibnr = None

        for line in output.split('\n'):
            if 'TOTAL_ULTIMATE_LATEST2:' in line:
                total_ultimate = float(line.split(':')[1].strip())
            elif 'TOTAL_IBNR_LATEST2:' in line:
                total_ibnr = float(line.split(':')[1].strip())

        if total_ultimate is None or total_ibnr is None:
            return {"passed": False, "error": "Could not parse total_ultimate_latest2 or total_ibnr_latest2 from output"}

        ultimate_match = abs(total_ultimate - gt_ultimate) < 10000
        ibnr_match = abs(total_ibnr - gt_ibnr) < 10000

        passed = ultimate_match and ibnr_match

        errors = []
        if not ultimate_match:
            errors.append(
                f"Total ultimate latest 2: expected {gt_ultimate:,.2f}, got {total_ultimate:,.2f}")
        if not ibnr_match:
            errors.append(
                f"Total IBNR latest 2: expected {gt_ibnr:,.2f}, got {total_ibnr:,.2f}")

        return {
            "passed": passed,
            "error": None if passed else "; ".join(errors),
            "total_ultimate_latest2": total_ultimate,
            "total_ibnr_latest2": total_ibnr
        }
    except Exception as e:
        return {"passed": False, "error": f"Validation error: {e}"}
