# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Result Analyzer Module for Bayesian Optimization Experiments.

This module handles post-processing of UV-VIS data and calculation of
optimization objectives (percent yield and product throughput).
"""

from typing import Tuple

from post_processing.post_process_uv_recording import post_process_uv_recording
from post_processing.average_absorbance import average_absorbance
from post_processing.calculate_percent_yield import calculate_percent_yield
from post_processing.calculate_concentration_in_reactor_bed import (
    calculate_concentration_in_the_reactor_bed,
)
from post_processing.calculate_product_throughput import calculate_product_throughput
from bayesian_optimizer.experiment_state import BoCampaignState, IterationState

def analyze_experiment_results(
    bo_campaign_state: BoCampaignState,
    iteration_state: IterationState,
    uv_vis_results_csv_path: str,
) -> Tuple[float, float, float, float]:
    """
    Analyze UV-VIS recording and calculate reaction metrics.

    parameters:
     - experiment_state: BoCampaignState object containing experimental parameters
     - iteration_state: IterationState object containing trial conditions and other state info
     - uv_vis_results_csv_path: Path to the UV-VIS results CSV file

    Returns:
        Tuple of (avg_abs_reactant, avg_abs_product, percent_yield, throughput)
    """
    bo_parameters = bo_campaign_state.bo_parameters
    trial_conditions = iteration_state.trial_conditions
    instrument_parameters = iteration_state.instrument_parameters

    # Process UV recording to extract steady-state region
    uv_vis_recording_post_processing_df = post_process_uv_recording(
        flow_rate = trial_conditions["flow_rate"],
        target_volume = bo_parameters["target_volume_through_reactor_bed"],
        uv_vis_absorbance_results_csv=uv_vis_results_csv_path,
        experiment_converged_early=iteration_state.converged_early
    )
    
    # Calculate average absorbances of both reactant and product in the steady-state region
    average_absorbance_reactant = average_absorbance(
        uv_vis_recording_post_processing_df, bo_parameters["reactant_wavelength"]
    )
    average_absorbance_product = average_absorbance(
        uv_vis_recording_post_processing_df, bo_parameters["product_wavelength"]
    )
    
    print(
        f"Average absorbance of our reactant in steady-state at the end of the reaction is {average_absorbance_reactant}"
    )
    print(
        f"Average absorbance of our product in steady-state at the end of the reaction is {average_absorbance_product}"
    )
    
    # Back-calculate product concentration in reactor bed (corrects for pump 4 dilution)
    concentration_product_mol_per_uL_reactor_bed = (
        calculate_concentration_in_the_reactor_bed(
            absorbance=average_absorbance_product,
            experiment_state=bo_campaign_state,
            iteration_state=iteration_state
        )
    )

    # Calculate percent yield using reactor bed concentrations (mol/L on both sides)
    product_percent_yield = calculate_percent_yield(
        concentration_product_mol_per_L=concentration_product_mol_per_uL_reactor_bed * 1e6,
        initial_concentration_mol_per_L=iteration_state.reactor_bed_concentration_uM / 1e6,
    )
    
    # Calculate product throughput
    product_throughput_nmol_per_min = calculate_product_throughput(
        concentration_product_mol_per_uL_reactor_bed,
        reactor_flow_rate_uL_per_min=(instrument_parameters["flow_rate_pump1"] + instrument_parameters["flow_rate_pump2"] + instrument_parameters["flow_rate_pump3"])
    )
    
    print(f"The percent yield of our product is {product_percent_yield} %")
    print(f"The throughput of our product is {product_throughput_nmol_per_min} nmol/min")
    
    return (
        average_absorbance_reactant,
        average_absorbance_product,
        product_percent_yield,
        product_throughput_nmol_per_min,
    )
