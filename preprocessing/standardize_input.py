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

from typing import Sequence, Tuple


def standardize_input(
    experiment_input: Sequence[float], ndp: int = 2
) -> Tuple[float, ...]:
    """
    The role of this script is to standardize our inputs before run_bayesian_optimization_iteration

    parameters:
     - input: Is a sequence with our flow rate, dilution_factor, temperature,
       co-solvent valve position, co-solvent fraction, and light intensity
     - ndp: Number of decimal places to round to for standardization

    return:
     - standardized_input: Standardized format of our input variables for the RESULTS_CACHE
    """

    standardized_experimental_parameters_input = tuple(
        round(float(experimental_parameter), ndp)
        for experimental_parameter in experiment_input
    )
    return standardized_experimental_parameters_input
