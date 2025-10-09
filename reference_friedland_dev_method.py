"""
Reference Implementation: Friedland XYZ Development Method
This script implements the complete chainladder development method and outputs
ground truth values for each step that will be used to validate AI-generated code.
"""

import pandas as pd
import numpy as np
import json
import chainladder as cl
from pathlib import Path


def convert_nan_to_none(obj):
    """Recursively convert NaN values to None for JSON serialization."""
    if isinstance(obj, dict):
        return {key: convert_nan_to_none(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_nan_to_none(item) for item in obj]
    elif isinstance(obj, float) and np.isnan(obj):
        return None
    else:
        return obj

def step_1_load_triangle():
    """
    Step 1: Load the triangle data and convert it to chainladder triangle
    Returns: chainladder Triangle object and raw dataframe
    """
    print("=" * 80)
    print("STEP 1: Load Triangle Data and Convert to Chainladder Triangle")
    print("=" * 80)
    
    data_path = Path(__file__).parent / "test_data" / "friedland_xyz_dev_method" / "reported_claims_triangle.csv"
    
    df = pd.read_csv(data_path, thousands=',')
    print("\nRaw data loaded:")
    print(df)
    
    df_clean = df.copy()
    df_clean = df_clean.rename(columns={'Accident Year': 'AccidentYear'})
    
    value_columns = [col for col in df_clean.columns if col != 'AccidentYear']
    for col in value_columns:
        df_clean[col] = pd.to_numeric(df_clean[col].astype(str).str.replace(',', ''), errors='coerce')
    
    df_clean = df_clean[df_clean['AccidentYear'].notna()]
    df_clean['AccidentYear'] = df_clean['AccidentYear'].astype(int)
    
    df_clean = df_clean.dropna(how='all', subset=value_columns)
    
    print("\nCleaned data (wide format):")
    print(df_clean)
    
    df_melted = df_clean.melt(id_vars=['AccidentYear'], var_name='development', value_name='values')
    df_melted = df_melted.dropna(subset=['values'])
    df_melted['development'] = df_melted['development'].astype(int)
    
    df_melted['origin'] = pd.to_datetime(df_melted['AccidentYear'], format='%Y')
    df_melted['valuation'] = df_melted.apply(
        lambda row: row['origin'] + pd.DateOffset(months=int(row['development'])-1), 
        axis=1
    )
    
    print("\nMelted (long) format with dates:")
    print(df_melted.head(20))
    
    triangle = cl.Triangle(
        df_melted,
        origin='origin',
        development='valuation',
        columns='values',
        cumulative=True
    )
    
    print("\nChainladder Triangle created:")
    print(triangle)
    
    print("\nTriangle shape:", triangle.shape)
    print("Triangle origin:", [int(str(x)[:4]) for x in triangle.origin])
    print("Triangle development:", [int(x) for x in triangle.development])
    
    ground_truth = {
        "triangle_shape": list(triangle.shape),
        "origins": [int(str(x)[:4]) for x in triangle.origin],
        "development_periods": [int(x) for x in triangle.development],
        "triangle_values": triangle.values[0, 0].tolist(),
        "latest_diagonal": triangle.latest_diagonal.values[0, 0, :, 0].tolist()
    }
    
    return triangle, df_clean, ground_truth


def step_2_weighted_average_ldfs(triangle, n_periods=3):
    """
    Step 2: Calculate weighted average LDFs using specified number of periods
    Uses Pipeline architecture to fit development patterns
    Returns: development estimator with fitted LDFs
    """
    print("\n" + "=" * 80)
    print(f"STEP 2: Calculate Weighted Average LDFs (using {n_periods} periods)")
    print("=" * 80)
    
    pipe = cl.Pipeline(
        steps=[
            ('dev', cl.Development(average='volume', n_periods=n_periods))
        ]
    )
    pipe.fit(triangle)
    
    ldfs_weighted = pipe.named_steps.dev.ldf_.values[0, 0, 0, :]
    
    print(f"\nWeighted Average LDFs (using {n_periods} periods):")
    for i, ldf in enumerate(ldfs_weighted):
        dev_period = triangle.development[i]
        print(f"  {dev_period}-to-{triangle.development[i+1] if i+1 < len(triangle.development) else 'Ult'}: {ldf:.6f}")
    
    ground_truth = {
        "n_periods_used": n_periods,
        "method": "volume_weighted",
        "ldfs": ldfs_weighted.tolist(),
        "development_ages": [int(x) for x in triangle.development[:-1]]
    }
    
    return pipe, ldfs_weighted, ground_truth


def step_3_simple_average_ldfs(triangle, n_periods=5):
    """
    Step 3: Calculate simple (straight) average LDFs using specified number of periods
    Uses Pipeline architecture to fit development patterns
    Returns: development pipeline with fitted LDFs
    """
    print("\n" + "=" * 80)
    print(f"STEP 3: Calculate Simple Average LDFs (using {n_periods} periods)")
    print("=" * 80)
    
    pipe = cl.Pipeline(
        steps=[
            ('dev', cl.Development(average='simple', n_periods=n_periods))
        ]
    )
    pipe.fit(triangle)
    
    ldfs_simple = pipe.named_steps.dev.ldf_.values[0, 0, 0, :]
    
    print(f"\nSimple Average LDFs (using {n_periods} periods):")
    for i, ldf in enumerate(ldfs_simple):
        dev_period = triangle.development[i]
        print(f"  {dev_period}-to-{triangle.development[i+1] if i+1 < len(triangle.development) else 'Ult'}: {ldf:.6f}")
    
    ground_truth = {
        "n_periods_used": n_periods,
        "method": "simple_average",
        "ldfs": ldfs_simple.tolist(),
        "development_ages": [int(x) for x in triangle.development[:-1]]
    }
    
    return pipe, ldfs_simple, ground_truth


def step_4_calculate_cdfs_with_tail(triangle, dev_pipe, tail_factor=1.00, from_age=132):
    """
    Step 4: Calculate CDFs (Cumulative Development Factors) by applying a tail factor
    Uses Pipeline architecture to chain Development and TailConstant estimators
    Returns: pipeline with tail applied and extracted CDFs
    """
    print("\n" + "=" * 80)
    print(f"STEP 4: Calculate CDFs with Tail Factor")
    print("=" * 80)
    
    print(f"\nApplying tail factor of {tail_factor:.2f} from age {from_age} to Ultimate")
    
    pipe = cl.Pipeline(
        steps=[
            ('dev', dev_pipe.named_steps.dev),
            ('tail', cl.TailConstant(tail=tail_factor))
        ]
    )
    pipe.fit(triangle)
    
    ldfs_with_tail = pipe.named_steps.tail.ldf_.values[0, 0, 0, :]
    cdfs = pipe.named_steps.tail.cdf_.values[0, 0, 0, :]
    
    print("\nLDFs with tail factor:")
    for i, ldf in enumerate(ldfs_with_tail):
        if i < len(ldfs_with_tail) - 1:
            print(f"  Age {12*(i+1)}-to-{12*(i+2)}: {ldf:.6f}")
        else:
            print(f"  Age {from_age}-to-Ult: {ldf:.6f}")
    
    print("\nCumulative Development Factors (CDFs):")
    for i, cdf in enumerate(cdfs):
        if i < len(cdfs) - 1:
            print(f"  Age {12*(i+1)}: {cdf:.6f}")
        else:
            print(f"  Age-to-Ult: {cdf:.6f}")
    
    ground_truth = {
        "ldfs_with_tail": ldfs_with_tail.tolist(),
        "tail_factor": tail_factor,
        "tail_from_age": from_age,
        "cdfs": cdfs.tolist()
    }
    
    return pipe, cdfs, ldfs_with_tail, ground_truth


def step_5_chainladder_method(triangle, dev_tail_pipe):
    """
    Step 5: Perform Chainladder method using the triangle and pipeline from step 4
    Uses complete Pipeline with Development, Tail, and Chainladder model
    Returns: ultimates by accident year
    """
    print("\n" + "=" * 80)
    print("STEP 5: Perform Chainladder Method and Calculate Ultimates")
    print("=" * 80)
    
    cdfs = dev_tail_pipe.named_steps.tail.cdf_.values[0, 0, 0, :]
    
    print("\nUsing CDFs from Step 4 (volume-weighted with tail factor):")
    for i, cdf in enumerate(cdfs):
        if i < len(triangle.development):
            print(f"  Age {triangle.development[i]}: {cdf:.6f}")
        else:
            print(f"  Age-to-Ult: {cdf:.6f}")
    
    pipe = cl.Pipeline(
        steps=[
            ('dev', dev_tail_pipe.named_steps.dev),
            ('tail', dev_tail_pipe.named_steps.tail),
            ('model', cl.Chainladder())
        ]
    )
    pipe.fit(triangle)
    
    ultimates = pipe.named_steps.model.ultimate_.values[0, 0, :, 0]
    
    print("\nUltimates by Accident Year:")
    for i, origin in enumerate(triangle.origin):
        print(f"  {origin}: ${ultimates[i]:,.2f}")
    
    total_ultimate = np.nansum(ultimates)
    print(f"\nTotal Ultimate: ${total_ultimate:,.2f}")
    
    ultimates_dict = {}
    for i, origin in enumerate(triangle.origin):
        origin_year = int(str(origin)[:4])
        ultimate_val = float(ultimates[i]) if not np.isnan(ultimates[i]) else None
        if ultimate_val is not None:
            ultimates_dict[origin_year] = ultimate_val
    
    ground_truth = {
        "cdfs_used": cdfs.tolist(),
        "ultimates_by_origin": ultimates_dict,
        "total_ultimate": float(total_ultimate)
    }
    
    return pipe, ultimates, ground_truth


def step_6_calculate_ibnr(triangle, model_pipe):
    """
    Step 6: Calculate IBNR (Incurred But Not Reported) reserves
    Uses the fitted pipeline from step 5 to extract IBNR
    Returns: IBNR by accident year and total
    """
    print("\n" + "=" * 80)
    print("STEP 6: Calculate IBNR")
    print("=" * 80)
    
    latest_values = triangle.latest_diagonal.values[0, 0, :, 0]
    ultimates = model_pipe.named_steps.model.ultimate_.values[0, 0, :, 0]
    ibnr = model_pipe.named_steps.model.ibnr_.values[0, 0, :, 0]
    
    print("\nIBNR by Accident Year:")
    for i, origin in enumerate(triangle.origin):
        if not np.isnan(ultimates[i]) and not np.isnan(latest_values[i]):
            print(f"  {origin}: Latest=${latest_values[i]:,.2f}, Ultimate=${ultimates[i]:,.2f}, IBNR=${ibnr[i]:,.2f}")
    
    total_ibnr = np.nansum(ibnr)
    total_latest = np.nansum(latest_values)
    print(f"\nTotal Latest: ${total_latest:,.2f}")
    print(f"\nTotal IBNR: ${total_ibnr:,.2f}")
    
    latest_dict = {}
    ibnr_dict = {}
    for i, origin in enumerate(triangle.origin):
        origin_year = int(str(origin)[:4])
        latest_val = float(latest_values[i]) if not np.isnan(latest_values[i]) else None
        ibnr_val = float(ibnr[i]) if not np.isnan(ibnr[i]) else None
        if latest_val is not None:
            latest_dict[origin_year] = latest_val
        if ibnr_val is not None:
            ibnr_dict[origin_year] = ibnr_val
    
    ground_truth = {
        "latest_values_by_origin": latest_dict,
        "ibnr_by_origin": ibnr_dict,
        "total_latest": float(total_latest),
        "total_ibnr": float(total_ibnr)
    }
    
    return ibnr, ground_truth


def main():
    """Execute all steps and save ground truth data"""
    print("\n" + "=" * 80)
    print("FRIEDLAND XYZ DEVELOPMENT METHOD - REFERENCE IMPLEMENTATION")
    print("=" * 80)
    
    all_ground_truth = {}
    
    triangle, df_clean, gt_step1 = step_1_load_triangle()
    all_ground_truth["step_1"] = gt_step1
    
    n_periods_weighted = 3
    dev_weighted_pipe, ldfs_weighted, gt_step2 = step_2_weighted_average_ldfs(triangle, n_periods=n_periods_weighted)
    all_ground_truth["step_2"] = gt_step2
    
    n_periods_simple = 5
    dev_simple_pipe, ldfs_simple, gt_step3 = step_3_simple_average_ldfs(triangle, n_periods=n_periods_simple)
    all_ground_truth["step_3"] = gt_step3
    
    tail_factor = 1.00
    dev_tail_pipe, cdfs_with_tail, ldfs_with_tail, gt_step4 = step_4_calculate_cdfs_with_tail(
        triangle,
        dev_weighted_pipe,
        tail_factor=tail_factor, 
        from_age=132
    )
    all_ground_truth["step_4"] = gt_step4
    
    model_pipe, ultimates, gt_step5 = step_5_chainladder_method(triangle, dev_tail_pipe)
    all_ground_truth["step_5"] = gt_step5
    
    ibnr, gt_step6 = step_6_calculate_ibnr(triangle, model_pipe)
    all_ground_truth["step_6"] = gt_step6
    
    all_ground_truth_clean = convert_nan_to_none(all_ground_truth)
    
    output_path = Path(__file__).parent / "test_data" / "friedland_xyz_dev_method" / "ground_truth.json"
    with open(output_path, 'w') as f:
        json.dump(all_ground_truth_clean, f, indent=2)
    
    print("\n" + "=" * 80)
    print("GROUND TRUTH SAVED")
    print("=" * 80)
    print(f"Ground truth data saved to: {output_path}")
    
    print("\n" + "=" * 80)
    print("SUMMARY OF GROUND TRUTH VALUES")
    print("=" * 80)
    print(json.dumps(all_ground_truth_clean, indent=2))


if __name__ == "__main__":
    main()

