# auto_zahrt/state.py
from pathlib import Path
from typing import Any, Dict, Tuple

from auto_zahrt.state import (
    EXPERIMENTAL_PARAMETERS,
    iteration,
    RESULTS_CACHE,
    bayesian_optimization_results_csv_path,
)

# Ax noise (SEM) used when reporting metrics
NOISE_SEM: float = 1e-3


def set_experimental_parameters(params: Dict[str, Any]) -> None:
    """from auto_zahrt.state import (
    EXPERIMENTAL_PARAMETERS,
    iteration,
    RESULTS_CACHE,
    bayesian_optimization_results_csv_path,
)

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
