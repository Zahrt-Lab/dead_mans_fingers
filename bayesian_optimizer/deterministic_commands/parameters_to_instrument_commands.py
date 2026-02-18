# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Experiment Setup Module for Bayesian Optimization.

This module handles parameter processing, validation, and file/directory setup
for a single Bayesian optimization iteration.
"""

from pathlib import Path
from typing import Tuple, Dict, Any
from preprocessing.constrain_to_search_space import constrain_to_search_space
from preprocessing.standardize_input import standardize_input
from preprocessing.parameters_to_commands import parameters_to_commands
from bayesian_optimizer.deterministic_commands.state import BO_EXPERIMENTAL_PARAMETERS


def parameters_to_instrument_commands(experiment: Tuple[float, ...]) -> Dict[str, Any]:
    """
    Process and validate experimental parameters.
    
    Constrains parameters to search space, standardizes input, and calculates
    instrument parameters needed for the experiment.
    
    Parameters:
        experiment: Tuple containing (flow_rate, dilution_factor, temperature, 
                    cosolvent_valve_position, fraction_of_cosolvent, light_intensity)
    
    Returns:
        Dictionary containing:
            - reactor_bed_flow_rate, dilution_factor, temperature, etc. (validated params)
            - reactor_bed_concentration_uM (calculated concentration)
            - experiment_check (standardized tuple for caching)
            - instrument_parameter (dict of pump flow rates, volumes, etc.)
    """
    # Constrain parameters to set search space bounds in case anything went out of bounds
    reactor_bed_flow_rate, dilution_factor, temperature, cosolvent_valve_position, \
        fraction_of_cosolvent, light_intensity = constrain_to_search_space(experiment)
    
    # Standardize for cache checking to make sure they are in the desired input format
    experiment_check = standardize_input(
        (reactor_bed_flow_rate, dilution_factor, temperature, cosolvent_valve_position, 
         fraction_of_cosolvent, light_intensity)
    )
    
    # Calculate reactor bed concentration based on dilution factor suggested by ax's BO
    reactor_bed_concentration_uM = dilution_factor * BO_EXPERIMENTAL_PARAMETERS["xylopyridine_analogs_concentrations_uM"]
    
    # Volume to flow through reactor which is deterministic, 
    # Can be less if the UV-detector finds the experiment meets termination conditions early
    volume = int(round(BO_EXPERIMENTAL_PARAMETERS["total_volume_through_reactor_bed"], 0))
    
    # Calculate instrument parameters
    instrument_parameter = parameters_to_commands(
        flow_rate_uL_per_min=reactor_bed_flow_rate,
        dilution_factor=dilution_factor,
        cosolvent_valve_position=int(cosolvent_valve_position),
        cosolvent_fraction=fraction_of_cosolvent,
        light_intensity=light_intensity,
        stock_concentration_uM=BO_EXPERIMENTAL_PARAMETERS["xylopyridine_analogs_concentrations_uM"],
        target_absorbance_in_the_uv_detector=BO_EXPERIMENTAL_PARAMETERS["target_absorbance_in_the_uv_detector"],
        max_absorbance_concentration_uM_uv_detector=BO_EXPERIMENTAL_PARAMETERS["max_absorbance_concentration_uM_uv_detector"],
        volume_uL=volume,
    )
    
    return {
        "reactor_bed_flow_rate": reactor_bed_flow_rate,
        "dilution_factor": dilution_factor,
        "temperature": temperature,
        "cosolvent_valve_position": cosolvent_valve_position,
        "fraction_of_cosolvent": fraction_of_cosolvent,
        "light_intensity": light_intensity,
        "reactor_bed_concentration_uM": reactor_bed_concentration_uM,
        "experiment_check": experiment_check,
        "volume": volume,
        "instrument_parameter": instrument_parameter,
    }


def setup_directories_and_paths(iteration_num: int) -> Dict[str, Path]:
    """
    Create directories and setup file paths for the experiment.
    
    Args:
        iteration_num: Current iteration number
    
    Returns:
        Dictionary containing all relevant paths:
            - base_directory
            - instrument_config
            - command_path_template
            - results_csv
            - reactor_bed_target_volume
    """
    base_directory = Path(BO_EXPERIMENTAL_PARAMETERS["base_directory"])
    base_directory.mkdir(parents=True, exist_ok=True)
    
    instrument_config = base_directory / "Instrument_Config_File.csv"
    command_path_template = base_directory / f"Fluorescent_Optimization_Iteration_{iteration_num}"
    
    # Build results CSV path using prefix and current analog name
    from bayesian_optimizer.deterministic_commands.state import CURRENT_XYLOPYRIDINE_ANALOG, bayesian_optimization_results_csv_path
    results_csv = Path(bayesian_optimization_results_csv_path(CURRENT_XYLOPYRIDINE_ANALOG))
    
    # Calculate reactor bed target volume
    volume = int(round(BO_EXPERIMENTAL_PARAMETERS["total_volume_through_reactor_bed"], 0))
    reactor_bed_target_volume = volume - 500
    
    print(f"The base directory is {base_directory}")
    print(f"The instrument config file is {instrument_config}")
    print(f"The fluorescent reaction command template is {command_path_template}")
    print(f"The fluorescent reaction bayesian optimization results saved to {results_csv}")
    print(f"Reactor bed target volume to reach before recording is {reactor_bed_target_volume}")
    
    return {
        "base_directory": base_directory,
        "instrument_config": instrument_config,
        "command_path_template": command_path_template,
        "results_csv": results_csv,
        "reactor_bed_target_volume": reactor_bed_target_volume,
    }
