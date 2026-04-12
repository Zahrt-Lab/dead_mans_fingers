# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
This script will standardize our inputs before run_bayesian_optimization_iteration
make sure their are no type or formatting issues
"""

from typing import Dict
from bayesian_optimizer.experiment_state import IterationState

def standardize_input(
    iteration_state: IterationState, ndp: int = 4
) -> IterationState:
    """
    The role of this script is to standardize our inputs before run_bayesian_optimization_iteration

    parameters:
     - iteration_state: The current state of the iteration, which includes the trial conditions that we want to standardize
       the trial conditions that we want to standardize
     - ndp: Number of decimal places to round to for standardization

    return:
     - standardized_input: Standardized format of our input variables for the RESULTS_CACHE
    """

    for key, value in iteration_state.trial_conditions.items():
        iteration_state.trial_conditions[key] = round(float(value), ndp)

    return iteration_state