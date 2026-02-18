# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

# bayesian_optimizer/state.py
from pathlib import Path
from typing import Any, Dict, Tuple

#TODO: I think the necessary changes have been made to this code to get it up and going

COMPLETE_WORKFLOW_PARAMETERS: Dict[str, Any] = {}

# Bayesian Optimization parameters to be filled at start of each individual campaign
BO_EXPERIMENTAL_PARAMETERS: Dict[str, Any] = {}

# Production Run parameters to be filled at start of each production run
PRODUCTION_RUN_EXPERIMENTAL_PARAMETERS: Dict[str, Any] = {}

# Iteration metadata / stock volumes
ITERATION: Dict[str, Any] = {
    "iteration #": 0,
    "pump1_xylopyridine_analogs_volume_stock_solution" : None,
    "pump2_0.1M_HCl_water_volume_stock_solution" : None,
    "pump3_co-solvents_volume_stock_solutions": None,
    "pump4_0.1M_HCl_water_volume_stock_solution" : None,
    "converged_early": False,
}

# Cache for multi-objective BO results
RESULTS_CACHE: Dict[Tuple[float, float, float, float, float, float], Tuple[float, float]] = {}

# Ax noise (SEM) used when reporting metrics
NOISE_SEM: float = 1e-3

# Simulation mode flag
SIMULATION_MODE: bool = None

# Current xylopyridine analog being optimized
CURRENT_XYLOPYRIDINE_ANALOG: str = ""

# This will select the xylopyrdine analog we are optimizing for in our campaign
# We will update this variable at the start of each optimization campaign for a
# specific xylopyridine analog
def set_bo_experimental_parameters(params: Dict[str, Any]) -> None:
    """
    Replace global BO_EXPERIMENTAL_PARAMETERS with a new mapping.
    """
    BO_EXPERIMENTAL_PARAMETERS.clear()
    BO_EXPERIMENTAL_PARAMETERS.update(params)

def set_production_run_experimental_parameters(params: Dict[str, Any]) -> None:
    """
    Replace global PRODUCTION_RUN_EXPERIMENTAL_PARAMETERS with a new mapping.
    """
    PRODUCTION_RUN_EXPERIMENTAL_PARAMETERS.clear()
    PRODUCTION_RUN_EXPERIMENTAL_PARAMETERS.update(params)

def set_noise_sem(value: float) -> None:
    """
    Update the global NOISE_SEM used for Ax metrics.
    """
    global NOISE_SEM
    NOISE_SEM = float(value)


def set_simulation_mode(value: bool) -> None:
    """
    Update the global SIMULATION_MODE flag.
    """
    global SIMULATION_MODE
    SIMULATION_MODE = bool(value)


def set_current_xylopyridine_analog(analog_name: str) -> None:
    """
    Update the global CURRENT_XYLOPYRIDINE_ANALOG name.
    """
    global CURRENT_XYLOPYRIDINE_ANALOG
    CURRENT_XYLOPYRIDINE_ANALOG = str(analog_name)


def bayesian_optimization_results_csv_path(xylopyridine_analogs: str) -> str:
    """
    Utility to compute the path where BO results are stored,
    ensuring the base directory exists.
    """
    base_directory = Path(BO_EXPERIMENTAL_PARAMETERS["base_directory"])
    base_directory.mkdir(parents=True, exist_ok=True)
    filename_prefix = BO_EXPERIMENTAL_PARAMETERS["Fluorescent_Bayesian_Optimization_results_filename"]
    file_name = f"{filename_prefix}_{xylopyridine_analogs}.csv"
    return str(
        base_directory
        / file_name
        )


def get_parameter_bounds() -> dict:
    """
    Extract all parameter bounds from experimental parameters.
    
    Returns:
        Dictionary containing min/max bounds for all optimization parameters:
        - flow_rate_min, flow_rate_max
        - dilution_factor_min, dilution_factor_max
        - temperature_min, temperature_max
        - co_solvent_min, co_solvent_max
        - co_solvent_volume_min, co_solvent_volume_max
        - light_intensity_min, light_intensity_max
    """
    flow_rate_min, flow_rate_max = BO_EXPERIMENTAL_PARAMETERS["flow_rate"]
    dilution_factor_min, dilution_factor_max = BO_EXPERIMENTAL_PARAMETERS["dilution_factor"]
    temperature_min, temperature_max = BO_EXPERIMENTAL_PARAMETERS["temperature"]
    co_solvent_min, co_solvent_max = BO_EXPERIMENTAL_PARAMETERS["cosolvents_valve_position"]
    co_solvent_volume_min, co_solvent_volume_max = BO_EXPERIMENTAL_PARAMETERS["co_solvent_dilution_factor"]
    light_intensity_min, light_intensity_max = BO_EXPERIMENTAL_PARAMETERS["light_intensity"]
    
    return {
        "flow_rate_min": flow_rate_min,
        "flow_rate_max": flow_rate_max,
        "dilution_factor_min": dilution_factor_min,
        "dilution_factor_max": dilution_factor_max,
        "temperature_min": temperature_min,
        "temperature_max": temperature_max,
        "co_solvent_min": co_solvent_min,
        "co_solvent_max": co_solvent_max,
        "co_solvent_volume_min": co_solvent_volume_min,
        "co_solvent_volume_max": co_solvent_volume_max,
        "light_intensity_min": light_intensity_min,
        "light_intensity_max": light_intensity_max,
    }
