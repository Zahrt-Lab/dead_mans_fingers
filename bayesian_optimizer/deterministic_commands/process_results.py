# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Results Processor Module for Bayesian Optimization.

This module handles post-processing of UV-Vis data, calculating percent yield
and throughput, and appending results to the CSV file.
"""

import time
from typing import Dict, Any, Tuple
from pathlib import Path
from bayesian_optimizer.deterministic_commands import state
from bayesian_optimizer.deterministic_commands.state import BO_EXPERIMENTAL_PARAMETERS, RESULTS_CACHE
from post_processing.post_process_uv_recording import post_process_uv_recording
from post_processing.average_absorbance import average_absorbance
from post_processing.calculate_percent_yield import calculate_percent_yield
from post_processing.calculate_concentration_in_reactor_bed import calculate_concentration_in_the_reactor_bed
from post_processing.calculate_product_throughput import calculate_product_throughput
from post_processing.append_bayesian_experimental_results import append_bayesian_experimental_results


def process_results(experiment_params: Dict[str, Any], iteration_num: int,
                    reactor_bed_target_volume: float, results_csv: Path) -> Tuple[float, float]:
    """
    Process UV-Vis data and calculate optimization objectives (yield & throughput).
    
    In hardware mode: post-processes UV recordings and calculates from absorbance data.
    In simulation mode: this function should not be called (returns are handled directly).
    
    Args:
        experiment_params: Dictionary containing all experiment parameters
        iteration_num: Current iteration number
        reactor_bed_target_volume: Target volume for UV recording analysis
        results_csv: Path to results CSV file for appending
    
    Returns:
        Tuple of (percent_yield, throughput_nmol_per_min)
    """
    reactant_wavelength = BO_EXPERIMENTAL_PARAMETERS["reactant_wavelength"]
    product_wavelength = BO_EXPERIMENTAL_PARAMETERS["product_wavelength"]
    reactor_bed_flow_rate = experiment_params["reactor_bed_flow_rate"]
    reactor_bed_concentration_uM = experiment_params["reactor_bed_concentration_uM"]
    experiment_check = experiment_params["experiment_check"]
    instrument_params = experiment_params["instrument_parameter"]
    
    print("Post-processing will occur to help select the absorbance after 3-5 residence times")
    
    # Post-process UV recordings from hardware
    uv_vis_recording_post_processing_df = post_process_uv_recording(
        reactor_bed_flow_rate,
        reactor_bed_target_volume,
        results_csv,
    )
    
    average_absorbance_reactant = average_absorbance(
        uv_vis_recording_post_processing_df, reactant_wavelength
    )
    average_absorbance_product = average_absorbance(
        uv_vis_recording_post_processing_df, product_wavelength
    )
    
    print(f"Average absorbance of our reactant at the end of the reaction is {average_absorbance_reactant}")
    print(f"Average absorbance of our product at the end of the reaction is {average_absorbance_product}")
    
    # Calculate initial concentration in mol/L for percent yield calculation
    initial_concentration_mol_per_L = reactor_bed_concentration_uM * 1e-6  # Convert µM to mol/L
    
    # Calculate percent yield
    product_percent_yield = calculate_percent_yield(
        average_absorbance_reactant,
        BO_EXPERIMENTAL_PARAMETERS["epsilon_reactant_at_lambda1_L_per_mol_cm"],
        average_absorbance_product,
        BO_EXPERIMENTAL_PARAMETERS["epsilon_product_at_lambda2_L_per_mol_cm"],
        BO_EXPERIMENTAL_PARAMETERS["pathlength_cm"],
        initial_concentration_mol_per_L,
    )
    
    # Calculate product concentration in the reactor bed
    concentration_product_mol_per_uL_reactor_bed = calculate_concentration_in_the_reactor_bed(
        absorbance=average_absorbance_product,
        volume_pump1_uL=instrument_params["volume_pump1"],
        volume_pump2_uL=instrument_params["volume_pump2"],
        volume_pump3_uL=instrument_params["volume_pump3"],
        volume_pump4_uL=instrument_params["volume_pump4"],
    )
    
    # Calculate product throughput
    reactor_flow_rate = (instrument_params["flow_rate_pump1"] + 
                         instrument_params["flow_rate_pump2"] + 
                         instrument_params["flow_rate_pump3"])
    
    product_throughput_nmol_per_min = calculate_product_throughput(
        concentration_product_mol_per_uL_reactor_bed,
        reactor_flow_rate_uL_per_min=reactor_flow_rate,
    )
    
    print(f"The percent yield of our product is {product_percent_yield} %")
    print(f"The throughput of our product is {product_throughput_nmol_per_min} nmol/min")
    
    return product_percent_yield, product_throughput_nmol_per_min


def save_results_to_csv(results_csv: Path, experiment_params: Dict[str, Any],
                        iteration_num: int, reactor_bed_target_volume: float,
                        percent_yield: float, throughput: float) -> None:
    """
    Append experimental results to the Bayesian optimization results CSV file.
    
    Args:
        results_csv: Path to CSV file
        experiment_params: Dictionary containing all experiment parameters
        iteration_num: Current iteration number
        reactor_bed_target_volume: Target volume used for analysis
        percent_yield: Calculated percent yield
        throughput: Calculated throughput in nmol/min
    """
    reactant_wavelength = BO_EXPERIMENTAL_PARAMETERS["reactant_wavelength"]
    product_wavelength = EXPERIMENTAL_PARAMETERS["product_wavelength"]
    experiment_check = experiment_params["experiment_check"]
    reactor_bed_concentration_uM = experiment_params["reactor_bed_concentration_uM"]
    
    # Get absorbance values (only applicable for hardware mode with actual UV data)
    # In simulation mode these would be 0 or calculated differently
    average_absorbance_reactant = 0  # Placeholder - in real use this comes from processing
    average_absorbance_product = 0   # Placeholder - in real use this comes from processing
    
    append_bayesian_experimental_results(
        results_csv,
        {
            "iteration": iteration_num,
            "flow_rate": experiment_check[0],
            "dilution_factor": experiment_check[1],
            "reactor_concentration_uM": round(reactor_bed_concentration_uM, 8),
            "temperature": experiment_check[2],
            "co_solvent": experiment_check[3],
            "co_solvent_volume": experiment_check[4],
            "light_intensity": experiment_check[5],
            "target_volume": reactor_bed_target_volume,
            "reactant_wavelength": reactant_wavelength,
            "product_wavelength": product_wavelength,
            "average_absorbance_reactant": average_absorbance_reactant,
            "average_absorbance_product": average_absorbance_product,
            "percent_yield": percent_yield,
            "throughput_nmol_per_min": throughput,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "ok",
            "error_message": "",
        },
    )
    
    print(f"Finished appending the results to csv file: {results_csv}")


def update_cache(experiment_check: tuple, percent_yield: float, throughput: float) -> None:
    """
    Update the results cache with experiment results for future lookup.
    
    Args:
        experiment_check: Standardized experiment parameters tuple
        percent_yield: Calculated percent yield
        throughput: Calculated throughput in nmol/min
    """
    RESULTS_CACHE[experiment_check] = (percent_yield, throughput)
