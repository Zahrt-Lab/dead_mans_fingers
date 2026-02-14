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

import pandas as pd


def extract_best_reaction_conditions(
    bo_results, yield_threshold
) -> tuple(float, float, float, float, float, float, float):
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

    bo_results_df_passed_threshold = bo_results_df[
        bo_results_df["percent_yield"] >= yield_threshold
    ]

    best_bo_result = bo_results_df_passed_threshold["throughput_nmol_per_min"].idxmax()

    return (
        float(best_bo_result["flow_rate_mL_per_min"]),
        float(best_bo_result["dilution_factor"]),
        float(best_bo_result["temperature_C"]),
        float(best_bo_result["cosolvent_valve_position"]),
        float(best_bo_result["fraction_of_cosolvent"]),
        float(best_bo_result["light_intensity_percent"]),
        float(best_bo_result["throughput_nmol_per_min"]),
    )
