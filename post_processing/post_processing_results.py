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
from bayesian_optimizer.deterministic_commands.state import BO_EXPERIMENTAL_PARAMETERS


def analyze_experiment_results(
    uv_vis_results_csv_path: str,
    converged_early: bool,
    reactor_bed_flow_rate: float,
    reactor_bed_target_volume: int,
    reactor_bed_concentration_uM: float,
    reactant_wavelength: int,
    product_wavelength: int,
    flow_rate_pump1: float,
    flow_rate_pump2: float,
    flow_rate_pump3: float,
    flow_rate_pump4: float,
) -> Tuple[float, float, float, float]:
    """
    Analyze UV-VIS recording and calculate reaction metrics.
    
    Args:
        uv_vis_results_csv_path: Path to UV-VIS data CSV
        converged_early: Whether the experiment converged early (use last 5 min of data)
        reactor_bed_flow_rate: Flow rate in reactor bed (uL/min)
        reactor_bed_target_volume: Target volume before recording (uL)
        reactor_bed_concentration_uM: Concentration in reactor bed (uM)
        reactant_wavelength: Wavelength for reactant (nm)
        product_wavelength: Wavelength for product (nm)
        flow_rate_pump1: Flow rate of pump 1 (uL/min)
        flow_rate_pump2: Flow rate of pump 2 (uL/min)
        flow_rate_pump3: Flow rate of pump 3 (uL/min)
        flow_rate_pump4: Flow rate of pump 4 (uL/min)
    
    Returns:
        Tuple of (avg_abs_reactant, avg_abs_product, percent_yield, throughput)
    """
    print("Post-processing will occur to help select the absorbance after 3-5 residence times")
    
    # Process UV recording to extract steady-state region
    uv_vis_recording_post_processing_df = post_process_uv_recording(
        reactor_bed_flow_rate,
        reactor_bed_target_volume,
        uv_vis_results_csv_path,
        converged_early
    )
    
    # Calculate average absorbances of both reactant and product in the steady-state region
    average_absorbance_reactant = average_absorbance(
        uv_vis_recording_post_processing_df, reactant_wavelength
    )
    average_absorbance_product = average_absorbance(
        uv_vis_recording_post_processing_df, product_wavelength
    )
    
    print(
        f"Average absorbance of our reactant in steady-state at the end of the reaction is {average_absorbance_reactant}"
    )
    print(
        f"Average absorbance of our product in steady-state at the end of the reaction is {average_absorbance_product}"
    )
    
    # Calculate percent yield
    product_percent_yield = calculate_percent_yield(
        average_absorbance_reactant,
        BO_EXPERIMENTAL_PARAMETERS["epsilon_reactant_at_lambda1_L_per_mol_cm"],
        average_absorbance_product,
        BO_EXPERIMENTAL_PARAMETERS["epsilon_product_at_lambda2_L_per_mol_cm"],
        BO_EXPERIMENTAL_PARAMETERS["pathlength_cm"],
        reactor_bed_concentration_uM / 1e6,  # Convert uM to mol/L
    )

    # TODO : Should probably update the names instead of using flow rate and volume
    # Calculate product concentration in reactor bed
    concentration_product_mol_per_uL_reactor_bed = (
        calculate_concentration_in_the_reactor_bed(
            absorbance=average_absorbance_product,
            volume_pump1_uL=flow_rate_pump1,  # Note: function may expect volumes not flow rates
            volume_pump2_uL=flow_rate_pump2,
            volume_pump3_uL=flow_rate_pump3,
            volume_pump4_uL=flow_rate_pump4
        )
    )
    
    # Calculate product throughput
    product_throughput_nmol_per_min = calculate_product_throughput(
        concentration_product_mol_per_uL_reactor_bed,
        reactor_flow_rate_uL_per_min=(flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3)
    )
    
    print(f"The percent yield of our product is {product_percent_yield} %")
    print(f"The throughput of our product is {product_throughput_nmol_per_min} nmol/min")
    
    return (
        average_absorbance_reactant,
        average_absorbance_product,
        product_percent_yield,
        product_throughput_nmol_per_min,
    )
