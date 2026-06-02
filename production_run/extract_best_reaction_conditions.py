# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
This script will extract the best reaction conditions from our bayesian optimization
campaign results and will then select the optimal experimental parameters to run in
our production run based.

The selection criteria for the optimal experimental parameters will be based on the
the product with the percent yield above the specified threshold (ex. 80%) that has the
highest throughput (moles of product produced per unit time) based on the optimizer
"""

from pathlib import Path

import pandas as pd


def extract_best_reaction_conditions(
    bo_results: Path, yield_threshold: float
) -> tuple:
    """
    This function will extract the best reaction conditions from our bayesian optimization
    campaign results and will then select the optimal experimental parameters to run in
    our production run based.
    
    The selection criteria for the optimal experimental parameters will be based on the
    the product with the percent yield above the specified threshold (ex. 80%) that has the
    highest throughput (moles of product produced per unit time) based on the optimizer

    parameters:
        - bo_results_df: The results from our bayesian optimization campaign that contains
          the experimental parameters and the corresponding yields and throughputs for each
          experiment.
        - yield_threshold: The percent yield threshold above which we want to consider the
          experimental parameters for our production run.

     - None
    """
    bo_results_df = pd.read_csv(bo_results)

    if bo_results_df.empty:
        raise ValueError(f"BO results CSV is empty: {bo_results}")

    bo_results_df_passed_threshold = bo_results_df[
        bo_results_df["percent_yield"] >= yield_threshold
    ]

    if bo_results_df_passed_threshold.empty:
        raise ValueError(
            f"No experiments met the yield threshold of {yield_threshold}%. "
            f"Max yield in results: {bo_results_df['percent_yield'].max():.1f}%"
        )

    best_row_idx = bo_results_df_passed_threshold["throughput_nmol_per_min"].idxmax()
    best_bo_result = bo_results_df_passed_threshold.loc[best_row_idx]

    return (
        float(best_bo_result["flow_rate"]),
        float(best_bo_result["dilution_factor"]),
        float(best_bo_result["temperature"]),
        float(best_bo_result["co_solvent_valve_position"]),
        float(best_bo_result["co_solvent_dilution_factor"]),
        float(best_bo_result["light_intensity"]),
        float(best_bo_result["throughput_nmol_per_min"]),
    )
