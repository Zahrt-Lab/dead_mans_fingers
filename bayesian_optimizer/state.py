# auto_zahrt/state.py
from pathlib import Path
from typing import Any, Dict, Tuple

# Global experiment parameters, filled at startup
EXPERIMENTAL_PARAMETERS: Dict[str, Any] = {}

# Iteration metadata / stock volumes
iteration: Dict[str, Any] = {
    "iteration #": 0,
    "last_temperature": None,
    "volume_stock_solution1": None,
    "volume_stock_solution2": None,
    "volume_stock_solution3": None,
}

# Cache for multi-objective BO results
RESULTS_CACHE: Dict[Tuple[float, float, float], Tuple[float, float]] = {}

# Ax noise (SEM) used when reporting metrics
NOISE_SEM: float = 1e-3


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


def bayesian_optimization_results_csv_path() -> str:
    """
    Utility to compute the path where BO results are stored,
    ensuring the base directory exists.
    """
    base_directory = Path(EXPERIMENTAL_PARAMETERS["base_directory"])
    base_directory.mkdir(parents=True, exist_ok=True)
    return str(
        base_directory
        / EXPERIMENTAL_PARAMETERS[
            "Fluorescent_Bayesian_Optimization_results_filename"
        ]
    )
