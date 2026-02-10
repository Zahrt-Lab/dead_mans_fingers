# bayesian_optimizer/state.py
from pathlib import Path
from typing import Any, Dict, Tuple

# Global experiment parameters, filled at startup
EXPERIMENTAL_PARAMETERS: Dict[str, Any] = {}

# TODO: Check to make sure the xylopyridine stock volume code is working to keep track of all the solvents
# TODO: Check to make sure this cosolvents stock volume code is working to keep track of all the solvents
# Iteration metadata / stock volumes
iteration: Dict[str, Any] = {
    "iteration #": 0,
    "xylopyridine_analog_volume_stock_solution": None,
    "pump1_0.1M_HCl_water_volume_stock_solution": None,
    "pump2_0.1M_HCl_water_volume_stock_solution": None,
}

# TODO : Decide if the xylopyridine stocks should be tracked here as well or in a different function on it's own
def initialize_cosolvent_volumes(number_of_cosolvents: int) -> None:
    """
    Initialize co-solvent volume tracking in iteration dictionary which is varaible in the code
    
    Parameters:
    - number_of_cosolvents: Number of co-solvents (1-6), this is dependent on the valve positions available
    
    Raises:
    - ValueError: If number_of_cosolvents is not in valid range
    """
    if not (1 <= number_of_cosolvents <= 6):
        raise ValueError(f"number_of_cosolvents must be between 1 and 6, got {number_of_cosolvents} cosolvents.")
    
    # Remove any existing cosolvent entries
    keys_to_remove = [key for key in iteration.keys() if key.startswith("cosolvent_")]
    for key in keys_to_remove:
        del iteration[key]
    
    # Add new cosolvent volume entries
    for i in range(1, number_of_cosolvents + 1):
        iteration[f"cosolvent_{i}_volume"] = None

# TODO : Decide if the xylopyridine stocks should be tracked here as well or in a different function on it's own
def get_cosolvent_volumes() -> Dict[str, float]:
    """
    Get all co-solvent volumes from iteration dict.
    
    Returns:
    - Dictionary of co-solvent volumes {cosolvent_1_volume: value, ...}
    """
    return {k: v for k, v in iteration.items() if k.startswith("cosolvent_")}

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


def bayesian_optimization_results_csv_path() -> str:
    """
    Utility to compute the path where BO results are stored,
    ensuring the base directory exists.
    """
    base_directory = Path(EXPERIMENTAL_PARAMETERS["base_directory"])
    base_directory.mkdir(parents=True, exist_ok=True)
    return str(
        base_directory
        / EXPERIMENTAL_PARAMETERS["Fluorescent_Bayesian_Optimization_results_filename"]
        )
