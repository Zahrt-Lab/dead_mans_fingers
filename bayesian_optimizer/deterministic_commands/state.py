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

# Global experiment parameters, filled at startup
EXPERIMENTAL_PARAMETERS: Dict[str, Any] = {}

# Iteration metadata / stock volumes
iteration: Dict[str, Any] = {
    "iteration #": 0,
    "pump1_xylopyridine_analogs_volume_stock_solution" : None,
    "pump2_0.1M_HCl_water_volume_stock_solution" : None,
    "pump3_co-solvents_volume_stock_solutions": None,
    "pump4_0.1M_HCl_water_volume_stock_solution" : None
}

# Cache for multi-objective BO results
RESULTS_CACHE: Dict[Tuple[float, float, float, float, float, float], Tuple[float, float]] = {}

# Ax noise (SEM) used when reporting metrics
NOISE_SEM: float = 1e-3

# Simulation mode flag
SIMULATION_MODE: bool = False


def set_experimental_parameters(params: Dict[str, Any]) -> None:
    """
    Replace global EXPERIMENTAL_PARAMETERS with a new mapping.
    """
    EXPERIMENTAL_PARAMETERS.clear()
    EXPERIMENTAL_PARAMETERS.update(params)


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


def bayesian_optimization_results_csv_path(xylopyridine_analogs: str) -> str:
    """
    Utility to compute the path where BO results are stored,
    ensuring the base directory exists.
    """
    base_directory = Path(EXPERIMENTAL_PARAMETERS["base_directory"])
    base_directory.mkdir(parents=True, exist_ok=True)
    file_name = EXPERIMENTAL_PARAMETERS["Fluorescent_Bayesian_Optimization_results_filename"] + f"_{xylopyridine_analogs}.csv"
    return str(
        base_directory
        / file_name
        )
